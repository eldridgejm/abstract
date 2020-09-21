with import <nixpkgs> {};

python37Packages.buildPythonApplication {
  name = "broadcast";
  src = ./.;

  # needed at runtime
  propagatedBuildInputs = with python37Packages; [ jinja2 ];

  # needed for development
  nativeBuildInputs = with python37Packages; [ pytest black ipython sphinx sphinx_rtd_theme ];

}
