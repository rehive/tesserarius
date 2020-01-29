tesserarius
-----------

tesserarius is a collection of invoke tasks that wrap common tools for creating
permissions for a team on the kubernetes cluster.

Installation
------------

To install, use pip::

    pip install tesserarius

Once installed, you can use it from within your project directory. The console
script uses an ``etc/tesserarius/tesserarius.yaml`` file to configure itself.

Prerequisites
-------------

The tesserarius tool is a python modules that uses invoke to make calls the
``kubectl`` and ``gcloud`` command-line tools. The following should be installed
before running tesserarius:

1. kubectl - Install the version matching the cluster you will be working.
2. gcloud - Ensure you login using ``gcloud auth login``
3. python - It is recommended you use python environment running Python 3.7.4 or later

Development
------------

1. Clone the repostory: ``git clone git@github.com:rehive/tesserarius``
2. Initialise your python environment: ``echo -n 'tesserarius' > .python-version && pyenv virtualenv 3.7.4 tesserarius``
3. Install pip with the following command ``pip install -e .``

Configuration
-------------

There are two main config files used to run the tool. All operations reference
contents of these config files. The first one is
``etc/tesserarius/tesserarius.yaml`` and the second one is used to keep track of
the roles ``etc/tesserarius/roles.yaml``

- The ``tesserarius.yaml`` config files includes all the settings for running the tesserarius::

		version: 1
		environment:
		  extensions:
			staging:
			  gcloud:
				project: project-id
				zone: europe-west1-c
			  kubernetes:
				cluster: staging
				namespace: service-test-staging
			production:
			  gcloud:
				project: project-id
				zone: europe-west1-c
			  kubernetes:
				cluster: production
				namespace: service-test
		  platform:
			staging:
			  gcloud:
				project: project-id
				zone: europe-west1-c
			  kubernetes:
				cluster: staging
				namespace: service-test-staging
			production:
			  gcloud:
				project: project-id
				zone: europe-west1-c
			  kubernetes:
				cluster: production
				namespace: service-test
		extensions:
		  serviceAccount:
		  - name: test-wale
			displayName: "test Service Backup Writer"
			description: "Service Account for the test Service on production to write to pgdata the bucket"
			role: extensions.bucket.writer
			environment: production
		  - name: test-staging-wale
			displayName: "test Service Backup Writer"
			description: "Service Account for the test Service on staging to write to pgdata the bucket"
			role: extensions.bucket.writer
			environment: staging
		  bindings: []
		  - members:
		    - user:test@rehive.com
		    role: projects/project-id/roles/extensions.team.developer
		platform: {}

- The ``roles.yaml`` file contains GCloud IAM role definitions::

        platform:
          roles:
          - name: platform.team.developer
            description: 'Developer role for GCP Users. Based on: Kubernetes Engine Developer'
            stage: ALPHA
            title: 'Platform Team Developer'
            addPermissions:
            - example.test.permission
            removePermissions: []
            permissions: []
        extensions:
          roles:
          - name: extensions.bucket.writer
            description: 'Role for Writing in GCS Buckets'
            stage: ALPHA
            title: 'Storage Bucket Writer'
            addPermissions:
            - example.test.permission
            removePermissions: []
            permissions: []

Commands
--------

The commands have been categorized between ``platform`` (to work on the ``rehive-core`` cluster) and ``extensions`` (to work on the ``rehive-services`` cluster)

List of available commands::

    Usage: tesserarius [--core-opts] <subcommand> [--subcommand-opts] ...

    Core options:

      --complete                     Print tab-completion candidates for given
                                     parse remainder.
      --hide=STRING                  Set default value of run()'s 'hide' kwarg.
      --write-pyc                    Enable creation of .pyc files.
      -d, --debug                    Enable debug output.
      -e, --echo                     Echo executed commands before running.
      -f STRING, --config=STRING     Runtime configuration file to use.
      -h [STRING], --help[=STRING]   Show core or per-task help and exit.
      -l, --list                     List available tasks.
      -n STRING, --project=STRING    The project/package name being build
      -p, --pty                      Use a pty when executing shell commands.
      -V, --version                  Show version and exit.
      -w, --warn-only                Warn, instead of failing, when shell commands
                                     fail.

    Subcommands:

      cluster.set                        Sets the active cluster
      extensions.bind                    Add IAM policy binding in rehive-services
      platform.bind                      Add IAM policy binding in rehive-services
      extensions.roles.create            Creates a Google Cloud IAM role on rehive-
                                         services
      extensions.roles.delete            Deletes a Google Cloud IAM role on rehive-
                                         services
      extensions.roles.update            Updates a Google Cloud IAM role on rehive-
                                         services
      extensions.serviceaccount.bind     Binds a Google Cloud IAM Service Account
                                         on rehive-services
      extensions.serviceaccount.create   Creates a Google Cloud IAM Service Account
                                         on rehive-services
      extensions.serviceaccount.delete   Deletes a Google Cloud IAM Service Account
                                         on rehive-services
      extensions.serviceaccount.update   Updates a Google Cloud IAM Service Account
                                         on rehive-services
      extensions.serviceaccount.upload   Uploads a Google Cloud IAM Service Account
                                         private key to kubernetes namespace
      platform.roles.create              Creates a Google Cloud IAM role on rehive-
                                         core
      platform.roles.delete              Deletes a Google Cloud IAM role on rehive-
                                         core
      platform.roles.update              Updates a Google Cloud IAM role on rehive-
                                         core
      platform.serviceaccount.bind       Binds a Google Cloud IAM Service Account
                                         on rehive-core
      platform.serviceaccount.create     Creates a Google Cloud IAM Service Account
                                         on rehive-core
      platform.serviceaccount.delete     Deletes a Google Cloud IAM Service Account
                                         on rehive-core
      platform.serviceaccount.update     Updates a Google Cloud IAM Service Account
                                         on rehive-core
      platform.serviceaccount.upload     Uploads a Google Cloud IAM Service Account
                                         private key to kubernetes namespace

- ``tesserarius extensions.serviceaccount.create``

	This command creates all the serviceaccounts listed in the config file
	under the ``extensions.serviceAccount`` list. It makes some checks to ensure that
	the names of the service account conform to the naming conventions set in for
	service account names (``<service-name>((-staging)?)(-<role_name>)?``)::

		Usage: tesserarius [--core-opts] extensions.serviceaccount.create [--options] [other tasks here ...]

		Docstring:
		  Creates a Google Cloud IAM Service Account on rehive-services

		Options:
		  -n STRING, --name=STRING   The name of the service account to handle

	You may create a specific serviceaccount by using ``-n | --name`` flag
	followed by the name of the service account. Eg.
	``tesserarius extensions.serviceaccount.create -n test-staging-media``


- ``tesserarius extensions.serviceaccounts.bind``

	Creates or updates the role binding for the serviceaccount with the role in
	the ``extensions.serviceaccount[i].role`` for all serviceaccounts in the config::

			Usage: tesserarius [--core-opts] extensions.serviceaccount.bind [--options] [other tasks here ...]

			Docstring:
			  Binds a Google Cloud IAM Service Account on rehive-services

			Options:
			  -n STRING, --name=STRING   The name of the service account to handle

	You may bind a specific serviceaccount by using ``-n | --name`` flag followed
	by the name of the service account.
	Eg. ``tesserarius extensions.serviceaccount.bind -n test-staging-media``

	The role referenced will be a custom role available under the
	rehive-services Google Cloud Project. It is advised to use the list of roles
	defined in the ``roles.yaml`` file.

- ``tesserarius extensions.serviceaccounts.delete``

	This command deletes all the serviceaccounts listed in the config file
	under the ``extensions.serviceAccount`` list::

			Usage: tesserarius [--core-opts] extensions.serviceaccount.delete [--options] [other tasks here ...]

			Docstring:
			  Deletes a Google Cloud IAM Service Account on rehive-services

			Options:
			  -n STRING, --name=STRING   The name of the service account to handle

	You may delete a specific serviceaccount by using ``-n | --name`` flag
	followed by the name of the service account.
	Eg. ``tesserarius extensions.serviceaccount.delete -n test-staging-media``

- ``tesserarius extensions.serviceaccount.upload``

	This command uploads a serviceaccount key listed in the config file under
	the ``extensions.serviceAccount`` list.
	Eg ``tesserarius extensions.serviceaccount.upload service-product-media product gcloud``::

			Usage: tesserarius [--core-opts] extensions.serviceaccount.upload [--options] [other tasks here ...]

			Docstring:
			  Uploads a Google Cloud IAM Service Account private key to
			  k8s namespace as a generic secret on rehive-services

			Options:
			  -n STRING, --name=STRING     The name of the service account to upload
			  -s STRING, --secret=STRING   The kubernetes secret name to upload the private
										   key

- ``tesserarius extensions.serviceaccount.update``

    This command updates all the serviceaccounts listed in the config file
    under the ``extensions.serviceAccount`` list. It makes some checks to ensure that
    the names of the service account conform to the naming conventions set in for
    service account names (``<service-name>((-staging)?)(-<role_name>)?``)
    It allows you to update an existing serviceaccount details::

			Usage: tesserarius [--core-opts] extensions.serviceaccount.update [--options] [other tasks here ...]

			Docstring:
			  Updates a Google Cloud IAM Service Account on rehive-services

			Options:
			  -n STRING, --name=STRING   The name of the service account to handle

	You may update a specific serviceaccount by using ``-n | --name`` flag
	followed by the name of the service account.
	Eg. ``tesserarius extensions.serviceaccount.update -n test-staging-media``

- ``tesserarius extensions.roles.create``

	This command creates all the roles listed in the config file under the
	``extensions.roles`` list. It makes some checks to ensure that the names of the
	service account conform to the naming conventions set in for service account
	names (``extensions.<service-name>(.<actor>)?``)::

			Usage: tesserarius [--core-opts] extensions.roles.create [--options] [other tasks here ...]

			Docstring:
			  Creates a Google Cloud IAM role on rehive-services

			Options:
			  -n STRING, --name=STRING   The name of the role to handle

- ``tesserarius extensions.roles.update``

	This command updates all the roles listed in the config file under the
	``extensions.roles`` list. It makes some checks to ensure that the names of the
	service account conform to the naming conventions set in for service account
	names (``extensions.<service-name>(.<actor>)?``)::

			Usage: tesserarius [--core-opts] extensions.roles.update [--options] [other tasks here ...]

			Docstring:
			  Updates a Google Cloud IAM role on rehive-services

			Options:
			  -n STRING, --name=STRING   The name of the role to handle

- ``tesserarius extensions.roles.delete``

	This command deletes all the roles listed in the config file under the
	``extensions.roles`` list. It makes some checks to ensure that the names of the
	service account conform to the naming conventions set in for service account
	names (``extensions.<service-name>(.<actor>)``)::

			Usage: tesserarius [--core-opts] extensions.roles.delete [--options] [other tasks here ...]

			Docstring:
			  Deletes a Google Cloud IAM role on rehive-services

			Options:
			  -n STRING, --name=STRING   The name of the role to handle
