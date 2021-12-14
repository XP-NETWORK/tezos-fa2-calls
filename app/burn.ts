import { MichelsonMap, TezosOperationError, TezosToolkit, VIEW_LAMBDA } from "@taquito/taquito";
import BigNumber from 'bignumber.js'
import { Tzip12Module } from '@taquito/tzip12'
import { InMemorySigner } from "@taquito/signer";
import { char2Bytes } from "@taquito/utils";

interface CollatzStorage {
  nft_cnt: BigNumber,
  xpnft_contract: string
}

require('dotenv').config()

const Tezos = new TezosToolkit(process.env.RPC_URL || "http://localhost:20000");
Tezos.addExtension(new Tzip12Module())

Tezos.setProvider({
  signer: new InMemorySigner(process.env.CREATOR_PK || "edsk3Z2t7t1XimympW62RmUDQeBxn9dw3pQdxxhpAGngmkjiFuXUAj")
});

(async () => {
  const xpnftContract = await Tezos.contract.at(process.env.XPNFT_ADDRESS || "")
  const collatzContract = await Tezos.contract.at(process.env.COLLATZ_ADDRESS || "")
  const owner = process.env.XPNFT_ADMIN

  const storage = await collatzContract.storage<CollatzStorage>()

  const metadata = new MichelsonMap();
  metadata.set("name", char2Bytes("Test"))
  metadata.set("symbol", char2Bytes("Test"))
  metadata.set("decimals", char2Bytes("0"))

  try {
    const tokenId = storage.nft_cnt.toNumber() - 1
    let op1 = await collatzContract.methods.burn(owner, tokenId).send({
      fee: 100_000,
      gasLimit: 800_000,
      storageLimit: 60_000,
    })
    console.log(`Waiting for ${op1.hash} to be confirmed...`)
    await op1.confirmation()

    const op2 = await Tezos.contract.originate({
      code: VIEW_LAMBDA.code,
      storage: VIEW_LAMBDA.storage,
    });

    const lambdaContract = await op2.contract();
    const lambdaContractAddress = lambdaContract.address;

    const response = await xpnftContract.views.balance_of([{
      owner: owner,
      token_id: tokenId
    }]).read(lambdaContractAddress)
    const balance = response[0].balance
    console.log(balance.toNumber())
  } catch (e) {
    // @ts-ignore
    console.error(e.message)
  }
})();