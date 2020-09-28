.PHONY: website
website: clean
	mkdir _build
	publish .. _build/published --skip-directories template
	abstract _build --published _build/published --now 2020-10-07

.PHONY: clean
clean:
	rm -rf _build
