export CXXFLAGS=-g
PROBS = a b c
TESTS = 0 1 2 3

P = $(@:%.$*=%)

.PHONY: $(PROBS) $(PROBS:%=%.%) %.test
$(PROBS):
	$(MAKE) -C $@ $@

$(PROBS:%=%.%):
	@cd $(P); \
	cp tests/$@.in $(P).in; \
	./$(P); \
	echo --$(@)--; \
	diff tests/$@.out $(P).out

%.:
	$(MAKE) $(TESTS:%=$*.%)
