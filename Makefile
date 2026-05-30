.PHONY: better-agents-install

better-agents-install: ; @echo "Installing better-agents..." ; rm -rf /tmp/better-agents ; git clone https://github.com/alphonse92/better-agents /tmp/better-agents ; bash /tmp/better-agents/install.sh ; rm -rf /tmp/better-agents