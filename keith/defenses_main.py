import argparse
from defenses import LangSentry
from test import DummyLLM, test_inputs

# Instantiate your LLM and LangSentry
llm = DummyLLM()
sentry = LangSentry(llm)

# Then run your proof-of-concept tests
def main():
    parser = argparse.ArgumentParser(
        description="Proof-of-Concept for LangSentry Defenses",
        epilog="Use --mode raw to see raw LLM outputs, --mode defended for outputs with defenses, or --mode both for side-by-side comparison."
    )
    parser.add_argument("--mode", choices=["raw", "defended", "both"], default="both",
                        help="Choose output mode: raw (LLM output without defenses), defended (with defenses), or both")
    args = parser.parse_args()

    for test in test_inputs:
        print(f"\nInput: {test}")
        raw_output = llm.generate(test)
        defended_output = sentry.process_input(test)
        if args.mode == "raw":
            print(f"Output (raw): {raw_output}")
        elif args.mode == "defended":
            print(f"Output (defended): {defended_output}")
        else:  # both
            print(f"Output (raw): {raw_output}")
            print(f"Output (defended): {defended_output}")
        print("-" * 50)

if __name__ == "__main__":
    main()
