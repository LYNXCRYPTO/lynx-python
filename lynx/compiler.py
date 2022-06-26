from solcx import compile_source, install_solc

install_solc("0.7.0")

compiledSol = compile_source(
        "contract Foo { function bar() public { return; } }",
        output_values=["abi", "bin"],
        solc_version="0.7.0"
    )
print(compiledSol)