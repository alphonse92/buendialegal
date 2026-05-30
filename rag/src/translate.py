import sys
import warnings
from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from common import build_llm

warnings.filterwarnings("ignore")


def load_prompt() -> str:
    return (Path(__file__).parent / "prompts" / "translate.md").read_text()


def translate(target_language: str, tone: str, phrase: str) -> str:
    prompt = ChatPromptTemplate.from_template(load_prompt())
    chain = prompt | build_llm() | StrOutputParser()
    return chain.invoke(
        {"target_language": target_language, "tone": tone, "phrase": phrase}
    ).strip()


def main(argv: list[str]) -> None:
    if len(argv) < 3:
        print(
            "Usage: python translate.py <target_language> <tone> <phrase words...>"
        )
        return

    target_language, tone = argv[0], argv[1]
    phrase = " ".join(argv[2:])
    print(translate(target_language, tone, phrase))


if __name__ == "__main__":
    main(sys.argv[1:])
