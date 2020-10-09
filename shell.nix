with import <nixpkgs> {};

let
  publish = python37Packages.buildPythonPackage {
    name = "publish";
    buildInputs = with python37Packages; [ pytest ];
    propagatedBuildInputs = with python37Packages; [ pyyaml cerberus ];
    src = fetchFromGitHub {
      owner = "eldridgejm";
      repo = "publish";
      rev = "c032605229fcb7be814f9fbbd5d51b3ec1aba246";
      sha256 = "10q2rb7k36f6cn2djajdsw72gpwq1scw8vggaqs2qd35qlxx8mjy";
    };
  };
in
  python37Packages.buildPythonApplication {
    name = "abstract";
    src = ./.;

    # needed at runtime
    propagatedBuildInputs = with python37Packages; [ jinja2 pyyaml markdown publish ];

    # needed for development
    nativeBuildInputs = with python37Packages; [ pytest black flake8 ipython sphinx sphinx_rtd_theme publish lxml ];

  }
