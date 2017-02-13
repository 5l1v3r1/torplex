with import <nixpkgs> {};

let

  stem = with python34Packages; buildPythonPackage rec {
    name = "stem-${version}";
    version = "1.5.4";
    src = fetchurl {
      url = "mirror://pypi/s/stem/${name}.tar.gz";
      sha256 = "1j7pnblrn0yr6jmxvsq6y0ihmxmj5x50jl2n2606w67f6wq16j9n";
    };
    propagatedBuildInputs = [ mock pyflakes pycodestyle pycrypto tox ];
  };

in stdenv.mkDerivation {
  name = "env";
  buildInputs = [
    stem
    python34
    python34Packages.pysocks
    python34Packages.requests2
  ] ++ lib.optional (!stdenv.isDarwin) tor;
  shellHook = ''
    export PYTHONPATH=.:$PYTHONPATH
  '';
}
