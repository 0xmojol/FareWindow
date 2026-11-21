import hashlib
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
POLICY_TEXT = (ROOT / "fixtures" / "septa_bus_metro_transfer.txt").read_text(
    encoding="utf-8"
)
POLICY_URL = (
    "https://raw.githubusercontent.com/0xmojol/FareWindow/"
    "main/fixtures/septa_bus_metro_transfer.txt"
)
AUTHORITY_URL = "https://www.septa.org/fares/"
POLICY_HASH = hashlib.sha256(POLICY_TEXT.encode("utf-8")).hexdigest()
POLICY_ID = "septa-bus-metro-v1"
SDK_VERSION = "v0.2.16"

SUPPORTED_RULE = {
    "status": "SUPPORTED",
    "window_minutes": 120,
    "max_free_transfers": 2,
    "eligible_modes": ["BUS", "METRO"],
    "eligible_payment_types": ["SEPTA_KEY", "CONTACTLESS"],
    "same_payment_method_required": True,
    "evidence_quote": (
        "Riders using a SEPTA Key card or contactless payment with a credit or debit card "
        "can make up to two transfers for free. These transfers must be made within two "
        "hours of the first tap. The same card must be used for all segments of the trip. "
        "Riders paying with cash or Quick Trip are not eligible for free transfers."
    ),
}


def deploy(direct_deploy):
    return direct_deploy(
        "contracts/fare_window.py",
        sdk_version=SDK_VERSION,
    )


def register_example(contract, policy_id=POLICY_ID):
    return contract.register_policy(
        policy_id,
        AUTHORITY_URL,
        POLICY_URL,
        POLICY_HASH,
    )


def mock_policy_page(direct_vm):
    direct_vm.mock_web(
        r"https://raw\.githubusercontent\.com/0xmojol/FareWindow/"
        r"main/fixtures/septa_bus_metro_transfer\.txt",
        {"status": 200, "body": POLICY_TEXT},
    )


def test_register_and_read_policy(direct_deploy):
    contract = deploy(direct_deploy)

    assert register_example(contract) == POLICY_ID

    policy = json.loads(contract.get_policy(POLICY_ID))
    assert policy["status"] == "REGISTERED"
    assert policy["policy"]["authority_url"] == AUTHORITY_URL
    assert policy["policy"]["snapshot_url"] == POLICY_URL
    assert policy["policy"]["snapshot_sha256"] == POLICY_HASH
    assert policy["rule"] == ""


def test_duplicate_policy_id_is_rejected(direct_deploy):
    contract = deploy(direct_deploy)
    register_example(contract)

    with pytest.raises(Exception, match="policy_id already exists"):
        register_example(contract)


def test_invalid_snapshot_hash_is_rejected(direct_deploy):
    contract = deploy(direct_deploy)

    with pytest.raises(Exception, match="64 hexadecimal"):
        contract.register_policy(
            POLICY_ID,
            AUTHORITY_URL,
            POLICY_URL,
            "not-a-sha256",
        )

    with pytest.raises(Exception, match="policy_id not found"):
        contract.get_policy(POLICY_ID)


def test_consensus_interprets_policy_and_checks_transfer(direct_vm, direct_deploy):
    contract = deploy(direct_deploy)
    register_example(contract)
    mock_policy_page(direct_vm)
    direct_vm.mock_llm(r".*", json.dumps(SUPPORTED_RULE))

    interpreted = json.loads(contract.interpret_policy(POLICY_ID))
    rule = json.loads(interpreted["rule"])

    assert interpreted["status"] == "ACTIVE"
    assert rule["window_minutes"] == 120
    assert rule["max_free_transfers"] == 2
    assert rule["eligible_modes"] == ["BUS", "METRO"]
    assert rule["eligible_payment_types"] == ["CONTACTLESS", "SEPTA_KEY"]

    accepted = json.loads(
        contract.check_transfer(
            "transfer-in-window",
            POLICY_ID,
            90,
            1,
            "BUS",
            "METRO",
            "SEPTA_KEY",
            True,
        )
    )
    assert accepted["outcome"] == "FREE_TRANSFER"

    rejected = json.loads(
        contract.check_transfer(
            "transfer-cash",
            POLICY_ID,
            30,
            1,
            "BUS",
            "METRO",
            "CASH",
            True,
        )
    )
    assert rejected["outcome"] == "FARE_APPLIES"
    assert rejected["reason"] == "payment type not eligible under policy"

    saved = json.loads(contract.get_case("transfer-in-window"))
    assert saved["policy_id"] == POLICY_ID
    assert saved["outcome"] == "FREE_TRANSFER"


def test_unclear_policy_stays_fail_closed(direct_vm, direct_deploy):
    contract = deploy(direct_deploy)
    register_example(contract)
    mock_policy_page(direct_vm)
    direct_vm.mock_llm(r".*", json.dumps({"status": "UNCLEAR"}))

    interpreted = json.loads(contract.interpret_policy(POLICY_ID))
    assert interpreted["status"] == "UNCLEAR"

    result = json.loads(
        contract.check_transfer(
            "transfer-unclear-policy",
            POLICY_ID,
            30,
            1,
            "BUS",
            "METRO",
            "SEPTA_KEY",
            True,
        )
    )
    assert result["outcome"] == "UNCLEAR"
    assert result["reason"] == "policy is not active"
