import os
import dotenv
import smartpy as sp

FA2 = sp.io.import_script_from_url('https://smartpy.io/templates/FA2.py')


class XPNFT(FA2.FA2):
    @sp.entry_point
    def mint(self, params):
        sp.set_type(
            params,
            sp.TRecord(
                token_id=sp.TNat,
                address=sp.TAddress,
                metadata=sp.TMap(
                    sp.TString, sp.TBytes
                ),
                amount=sp.TNat
            )
        )

        sp.verify(self.is_administrator(sp.sender),
                  message=self.error_message.not_admin())
        # We don't check for pauseness because we're the admin.
        if self.config.single_asset:
            sp.verify(params.token_id == 0,
                      message="single-asset: token-id <> 0")
        if self.config.non_fungible:
            sp.verify(params.amount == 1, message="NFT-asset: amount <> 1")
            sp.verify(
                ~ self.token_id_set.contains(
                    self.data.all_tokens, params.token_id),
                message="NFT-asset: cannot mint twice same token"
            )
        user = self.ledger_key.make(params.address, params.token_id)
        with sp.if_(self.data.ledger.contains(user)):
            self.data.ledger[user].balance += params.amount
        with sp.else_():
            self.data.ledger[user] = FA2.Ledger_value.make(params.amount)
        with sp.if_(~ self.token_id_set.contains(self.data.all_tokens, params.token_id)):
            self.token_id_set.add(self.data.all_tokens, params.token_id)
            self.data.token_metadata[params.token_id] = sp.record(
                token_id=params.token_id,
                token_info=params.metadata
            )
        if self.config.store_total_supply:
            self.data.total_supply[params.token_id] = params.amount + \
                self.data.total_supply.get(params.token_id, default_value=0)

    @sp.entry_point
    def burn(self, params):
        sp.set_type(params, sp.TRecord(token_id=sp.TNat, address=sp.TAddress, amount=sp.TNat))
        sp.verify(self.is_administrator(sp.sender), message = self.error_message.not_admin())
        # We don't check for pauseness because we're the admin.
        if self.config.single_asset:
            sp.verify(params.token_id == 0, message = "single-asset: token-id <> 0")
        if self.config.non_fungible:
            sp.verify(params.amount == 1, message = "NFT-asset: amount <> 1")
            # sp.verify(
            #     ~ self.token_id_set.contains(self.data.all_tokens, params.token_id),
            #     message = "NFT-asset: cannot mint twice same token"
            # )
        user = self.ledger_key.make(params.address, params.token_id)
        with sp.if_(self.data.ledger.contains(user)):
            self.data.ledger[user].balance = sp.as_nat(self.data.ledger[user].balance - params.amount)
        with sp.else_():
            self.data.ledger[user] = FA2.Ledger_value.make(params.amount)
            
        sp.verify(self.token_id_set.contains(self.data.all_tokens, params.token_id), "token-id doesn't exists.")
            
        if self.config.store_total_supply:
            self.data.total_supply[params.token_id] = sp.as_nat(self.data.total_supply.get(params.token_id, default_value = 0) - params.amount)


@sp.add_test(name="xpnet_test")
def test():
    sc = sp.test_scenario()
    sc.table_of_contents()
    FA2_admin = sp.test_account("FA2_admin")
    sc.h1("FA2")
    xp_nft = XPNFT(
        FA2.FA2_config(),
        admin=FA2_admin.address,
        metadata=sp.utils.metadata_of_url("https://example.com")
    )
    sc += xp_nft
    
    sc.h2("Mint")
    alice = sp.test_account("Alice")
    md = XPNFT.make_metadata(
        name="The Token Zero",
        decimals=0,
        symbol="TK0"
    )
    xp_nft.mint(
        token_id=0,
        address=alice.address,
        metadata=md,
        amount=1
    )


if __name__ == '__main__':
    dotenv.load_dotenv('.env')

    config = FA2.FA2_config(non_fungible=True)

    sp.add_compilation_target(
        "xpnft_comp",
        XPNFT(
            admin=sp.address(os.environ.get("XPNFT_ADMIN")),
            config=config,
            metadata=sp.utils.metadata_of_url("https://example.com")
        )
    )
