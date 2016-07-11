all: test


ifeq ($(OSNAME), Linux)
OPEN_COMMAND		:= gnome-open
OSDEPS			:= sudo apt-get update && sudo apt-get -y install libssl-dev python-dev libgnutls28-dev libtool  build-essential file libmysqlclient-dev libffi-dev libev-dev libevent-dev libxml2-dev libxslt1-dev libnacl-dev redis-tools vim htop aptitude lxc-docker-1.9.1 figlet supervisor virtualenvwrapper
else
OPEN_COMMAND		:= open
OSDEPS			:= brew install redis libevent libev
endif

filename=plant-`python -c 'import plant.version;print plant.version.version'`.tar.gz

export PYTHONPATH:=${PWD}
export PYTHONDONTWRITEBYTECODE:=x

test: clean unit functional

test-kind:
	@echo "Running unit tests"
	@nosetests --cover-branches --rednose --with-coverage  --cover-erase --cover-package=plant --stop -v -s tests/$(kind)

unit:
	@make test-kind kind=unit

functional:
	@make test-kind kind=functional

unit: clean

docs:
	cd docs && make html
	$(OPEN_COMMAND) docs/build/html/index.html

clean:
	@printf "Cleaning up files that are already in .gitignore... "
	@for pattern in `cat .gitignore`; do rm -rf $$pattern; find . -name "$$pattern" -exec rm -rf {} \;; done
	@echo "OK!"

release: test
	@./.release
	@make publish

publish:
	@python setup.py sdist register upload

prepare:
	@mkdir -p output
