with import <nixpkgs> {};

let

  stem = python27Packages.buildPythonPackage rec {
    name = "stem-${version}";
    version = "1.5.4";
    src = fetchurl {
      url = "mirror://pypi/s/stem/${name}.tar.gz";
      sha256 = "1j7pnblrn0yr6jmxvsq6y0ihmxmj5x50jl2n2606w67f6wq16j9n";
    };
    propagatedBuildInputs = with python27Packages; [ mock pyflakes pycodestyle pycrypto tox ];
    # buildInputs = [ tor ];
    # patchPhase = ''
    #   echo "from collections import OrderedDict" > stem/util/ordereddict.py
    # '';
  };

in stdenv.mkDerivation {
  name = "env";
  buildInputs = [
    python27
    python27Packages.requests2
    python27Packages.pysocks
    stem
  ];
  shellHook = ''
    export PYTHONPATH=.:$PYTHONPATH
  '';
}
