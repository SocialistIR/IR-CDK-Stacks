from socialist_ir.socialist_ir import SocialistIr


def main() -> None:
    ir = SocialistIr(name="main", required_variables=["account", "region"])
    ir.run()


if __name__ == "__main__":
    main()
