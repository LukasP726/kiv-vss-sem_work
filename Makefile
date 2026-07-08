NETLOGO ?= /opt/NetLogo-7.0.3

.PHONY: baseline extended experiments all clean visualize

baseline:
	./scripts/run_all_baselines.sh "$(NETLOGO)"

extended:
	./scripts/run_extended_experiments.sh "$(NETLOGO)"

experiments:
	./scripts/run_all_experiments.sh "$(NETLOGO)"

all: experiments

clean:
	rm -f out/*.csv out/*.log

visualize:
	python3 scripts/visualize_results.py --input-dir out --output-dir out/figures
