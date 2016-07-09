:title: Getting started with LetsEncrypt
:slug: getting-started-letsencrypt
:tags: letsencrypt, ansible, subsonic, weechat
:date: 2016-07-08 22:19:22

`LetsEncrypt <https://letsencrypt.org/>`_ really changed the SSL game, offering free certificates, but more than that offering them in a programatic way thus paving the way for a decent automation story. However the official client, now known as `certbot <https://certbot.eff.org/>`_, is lacking on certain features. Luckily there are a slew of clients that speak the `ACME <https://ietf-wg-acme.github.io/acme/>`_ protocol. After fiddling around with a few clients I wound up settling on a client written in Go named `Lego <https://github.com/xenolf/lego>`_.

`Obtaining the cert`_
=====================
I wanted a central location to manage my certificate lifecycle as well as having a single repository to handle the orchestration of the deployment of such certificates. As such, the default mechanism of dropping a challenge file in a webroot wouldn't work, as well as a few of the things I run don't lend itself to such an auth mechanism. In favor of this, I decided to leverage `dns-01 <https://ietf-wg-acme.github.io/acme/#rfc.section.7.4>`_ instead.

I like things tidy, so I keep everything inside of a directory structure as follows in ``/opt/``:

::

    lego
    ├── ansible // Where I keep the installation automation playbooks
    │   └── roles
    │       ├── host1
    │       │   ├── files
    │       │   ├── handlers
    │       │   └── tasks
    │       ├── host2
    │       │   ├── files
    │       │   ├── handlers
    │       │   └── tasks
    │       └── host3
    │           ├── files
    │           ├── handlers
    │           └── tasks
    ├── bin // Lego bin lives here and misc scripts
    └── data // Where Lego writes its goods
        ├── accounts
            │   └── acme-v01.api.letsencrypt.org
                │       └── email@example.com
                    │           └── keys
                        └── certificates // Here be certs

Since I am using the ``dns-01`` challenge with AWS Route53, the following environment variables must be defined: ``AWS_ACCESS_KEY_ID`` and ``AWS_SECRET_ACCESS_KEY``. Ensure there is a proper IAM role defined for this task, as well a corresponding policy. The Lego README provides an example policy which will get you going:

::

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "route53:GetChange",
                    "route53:ListHostedZonesByName"
                ],
                "Resource": [
                    "*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "route53:ChangeResourceRecordSets"
                ],
                "Resource": [
                    "arn:aws:route53:::hostedzone/<INSERT_YOUR_HOSTED_ZONE_ID_HERE>"
                ]
            }
        ]
    }

If you have multiple domains, in the second resource block just add a second ARN in a comma separated list. Or if you are less particular in doing things right and want to be looser on security, add ``arn:aws:route53:::hostedzone/*`` to allow modifications to all domains.

With that done, we can finally get our certs! This is as simple as::

    AWS_ACCESS_KEY_ID="<accessid>" AWS_SECRET_ACCESS_KEY="<secretkey>" /opt/lego/bin/lego -a --path="/opt/lego/data/" --email="email@example.com" --domain="domain.com" --dns route53 run

Arguments are:
    -a        Acknowledges that you agree to the current LetsEncrypt terms of service
    --path    Where to stick the certs and account information
    --email   The identity you want to use to register the cert with, they send you things like expiration notices
    --domain  The domain you want to get the cert for
    --dns     Specifies the DNS challenge, in this case route 53

You will notice that it both creates the DNS resource record to satisfy the challenge, and if everything went swimmingly will cleanup said record leaving things nice and tidy.

`Renewing the certs`_
=====================
With the cert obtained, we need to ensure that the certs get renewed with the standard 90 day life of a LetsEncrypt certificate. This is as simple as changing ``run`` to ``renew`` and adding ``--days 30`` to renew it within 30 days of expiration.

But since we want to automate this, lets make a little script to do this for us:

::

    #!/bin/bash
    
    DOMAINS="example.com example.org example.net""
    AWS_ACCESS_KEY_ID="<access_key>"
    AWS_SECRET_ACCESS_KEY="<secret_key>"
    
    for domain in $DOMAINS; do
        /opt/lego/bin/lego -a --path="/opt/lego/data/" --email="email@example.com" --domains="$domain" --dns route53 renew --days 30
        done

This will iterate through the list of ``$DOMAINS`` and will renew each one. I threw this in a cronjob to run every night, but a systemd timer is nice too if you swing that way.

`Installing the certs`_
=======================

There probably is a more elegant way of approaching this, but Ansible seemed perfect for what is being done here. It will ensure the certs are placed on the remote servers, and will execute actions if an update has happened and will noop otherwise. A basic boilerplate requires your `inventory <http://docs.ansible.com/ansible/intro_inventory.html>`_ defined, I call mine `hosts.ini`. In my playbook I define each host as a role to customize how each server needs to be handled. My playbook ``certificates.yaml`` looks as follows::

    - hosts: host1
      sudo: yes
      roles:
          - {role: 'roles/host1'}
    
Inside of each role's ``files`` directory I then symlink the cert and key in ``/opt/lego/data/certificates/`` and define the specific installation plays in ``tasks``.

Once your playbook looks and acts reasonably, cron it out::

    ansible-playbook -i /opt/lego/ansible/hosts.ini /opt/lego/ansible/certificates.yaml > /dev/null

`Installation for Subsonic`_
----------------------------
Since `Subsonic <http://subsonic.org>`_ runs java, we have to deal with the goofy keytool shenanigans. So the task I have defined for this server resembles::

    ---
    - name: Install certs
      copy: src={{ item }} dest=/opt/subsonic/ssl/{{ item }} mode=0600
      with_items:
          - subsonic.example.com.crt
          - subsonic.example.com.key
      notify:
          - generate keystore
          - restart subsonic

With a ``handler`` definition resembling the following::
    
    - name: generate keystore
      shell: /opt/subsonic/ssl/keytool.sh
    
    - name: restart subsonic
      service: name=subsonic state=restarted

keytool.sh is just a simple incarnation of the commands to convert the pems into the format that java is happy with::

    #!/bin/bash
    
    /usr/bin/openssl pkcs12 -in /opt/subsonic/ssl/subsonic.example.com.crt -inkey /opt/subsonic/ssl/subsonic.example.com.key key -export -out /opt/subsonic/ssl/subsonic.pkcs12 -password pass:subsonic
    
    /usr/bin/keytool -importkeystore -srckeystore /opt/subsonic/ssl/subsonic.pkcs12 -destkeystore /opt/subsonic/ssl/subsonic.keystore -srcstoretype PKCS12 -srcstorepass subsonic -deststorepass subsonic -srcalias 1 -destalias subsonic
    
    /usr/bin/zip -j /opt/subsonic/subsonic-booter-jar-with-dependencies.jar /opt/subsonic/ssl/subsonic.keystore
    
    /bin/rm /opt/subsonic/ssl/subsonic.keystore /opt/subsonic/ssl/subsonic.pkcs12


`Installation for weechat`_
---------------------------
The very capable IRC client `weechat <https://weechat.org/>`_ has a relay protocol allowing for remote access to the client from other things, such as a mobile browser such as `Glowing Bear <https://www.glowing-bear.org/>`_ which I use to access IRC from my iOS devices.

This assumes weechat relay is already set up, to start encrypting programatically we need a task defined similiar to::

    - name: Install certs for weechat
      copy: src={{ item }} dest=/home/taco/.weechat/certs/{{ item }} mode=600
      with_items:
          - weechat.example.com.crt
          - weechat.example.com.key
      notify:
          - reload weechat certs

And a handler such as::

    - name: reload weechat certs
      shell: /home/taco/.weechat/reloadcert.sh

Since ``reloadcert.sh`` will send a ``/relay sslcertkey`` via the fifo channel, ensure your weechat has it enabled with ``plugins.var.fifo.fifo = on``. If it's on inside your ``.weechat`` directory you will find a file resembling ``weechat_fifo_123`` with the suffix numbers indicating pid.

::

    #!/bin/bash
    
    cat /home/taco/.weechat/certs/weechat.example.com.key /home/taco/.weechat/certs/weechat.example.com.crt > /home/taco/.weechat/certs/relay.pem
    for fifo in /home/taco/.weechat/weechat_fifo_*
    do
        printf '%b' '*/relay sslcertkey\n' > "$fifo"
    done

This will send the reload to all running weechat instances, but is mostly harmless if the certpaths are configured correctly.
