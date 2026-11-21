def test_transfer_at_exact_window_boundary_is_free(direct_vm, direct_deploy):
    contract = deploy(direct_deploy)
    register_example(contract)
    mock_policy_page(direct_vm)
    direct_vm.mock_llm(r".*", json.dumps(SUPPORTED_RULE))

    interpreted = json.loads(contract.interpret_policy(POLICY_ID))
    assert interpreted["status"] == "ACTIVE"

    result = json.loads(
        contract.check_transfer(
            "transfer-exactly-120-minutes",
            POLICY_ID,
            120,
            1,
            "BUS",
            "METRO",
            "SEPTA_KEY",
            True,
        )
    )

    assert result["outcome"] == "FREE_TRANSFER"
