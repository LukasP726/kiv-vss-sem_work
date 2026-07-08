NETLOGO ?= /opt/NetLogo-7.0.3

.PHONY: baseline extended experiments all clean

baseline:
	./scripts/run_all_baselines.sh "$(NETLOGO)"

extended:
	./scripts/run_extended_experiments.sh "$(NETLOGO)"

experiments:
	./scripts/run_all_experiments.sh "$(NETLOGO)"

all: experiments

clean:
	rm -f out/*.csv out/*.log
