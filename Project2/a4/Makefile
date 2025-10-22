DIR := a4
ARCHIVE := $(DIR).zip

.PHONY: compress
compress:
	@echo "Creating $(ARCHIVE) from current folder..."
	@cd .. && zip -r $(ARCHIVE) $(DIR) -x "$(DIR)/venv/*" "$(DIR)/.git/*"
	@echo "Done! Created $(ARCHIVE) in parent directory."

.PHONY: clean
clean:
	rm -f ../$(ARCHIVE)
