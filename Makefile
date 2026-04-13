NETLOGO ?= /opt/NetLogo-7.0.3

.PHONY: baseline extended all clean

baseline:
	./scripts/run_all_baselines.sh "$(NETLOGO)"

extended:
	./scripts/run_extended_experiments.sh "$(NETLOGO)"

all: baseline extended

clean:
	rm -f out/*.csv out/*.log
