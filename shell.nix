with import <nixpkgs> {};

let
  publish = python37Packages.buildPythonApplication {
    name = "publish";
    propagatedBuildInputs = with python37Packages; [ cerberus pyyaml ];
    src = fetchFromGitHub {
      owner = "eldridgejm";
      repo = "publish";
      rev = "251ab3f7b8c3fd190cb79b16d62005453187bfc4";
      sha256 = "1s5618506ph1bpwj82y9m08zqrw3q0v8qckrm6jdjvwxrx5c7vxq";
    };
  };
in
  python37Packages.buildPythonApplication {
    name = "broadcast";
    src = ./.;

    # needed at runtime
    propagatedBuildInputs = with python37Packages; [ jinja2 markdown publish ];

    # needed for development
    nativeBuildInputs = with python37Packages; [ pytest black ipython sphinx sphinx_rtd_theme ];

  }
