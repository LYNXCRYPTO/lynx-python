from lynx.consensus.vdf import VDF

def test_vdf():
    # output = VDF.create_vdf(a=2, t=16, data="test")
    # print(f'n: {output[0]}')
    proof = VDF.sequential_squaring(n=713, a=2, t=16)
    print(proof)

if __name__ == "__main__":
    test_vdf()