import os
import dotenv
import smartpy as sp


def call(c, x):
    sp.transfer(x, sp.mutez(0), c)


class Collatz(sp.Contract):
    def __init__(self, xpnft_address):
        self.init(
            xpnft_contract=xpnft_address,
            nft_cnt=sp.nat(0)
        )
    
    @sp.entry_point
    def mint(self, params):
        sp.set_type(params.to, sp.TAddress)
        sp.set_type(params.data, sp.TBigMap(sp.TString, sp.TBytes))
        
        tk = sp.TRecord(
            address=sp.TAddress,
            amount=sp.TNat,
            metadata=sp.TBigMap(
                sp.TString, sp.TBytes
            ),
            token_id=sp.TNat
        )
        mint_entrypoint = sp.contract(tk, self.data.xpnft_contract, "mint").open_some()
        mint_args = sp.record(
            address=params.to,
            amount=sp.nat(1),
            metadata=params.data,
            token_id=self.data.nft_cnt
        )
        call(mint_entrypoint, mint_args)
        
        self.data.nft_cnt += sp.nat(1)


@sp.add_test(name="collatz_test")
def test():
    dotenv.load_dotenv(".env")
    
    scenario = sp.test_scenario()
    scenario.h1("Collatz - Inter-Contract Calls")
    
    xpnft_address = os.environ.get("XPNFT_ADDRESS")
    collatz = Collatz(
        xpnft_address=sp.address(xpnft_address)
    )
    scenario += collatz
    collatz.mint(
        to=sp.address(os.environ.get("XPNFT_ADMIN")),
        data=sp.utils.metadata_of_url("https://example.com")
    )

if __name__ == '__main__':
    dotenv.load_dotenv(".env")
    xpnft_address = os.environ.get("XPNFT_ADDRESS")
    sp.add_compilation_target(
        "collatz_comp",
        Collatz(
            xpnft_address=sp.address(xpnft_address)
        )
    )