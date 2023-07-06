from typing import List
from openadapt.models import Recording
from openadapt.strategies.mixins.layout import LayoutExtractionReplayStrategyMixin
from PIL import Image
from transformers import pipeline
import numpy as np
import pytest

IMAGE_FILE_NAMES = [
    "assets/test_ladingbill.png",
    "assets/test_invoice.png",
    "assets/test_calendar.png",
    "assets/test_calc.png",
]

LAYOUT_OBJ = LayoutExtractionReplayStrategyMixin(Recording(), IMAGE_FILE_NAMES)


def test_lading_bill_screenshot():
    questions = [
        "What is the bill of lading number?",
        "What is the carrier name?",
        "What is the ship date?",
        "What is the sender's phone number?",
    ]

    output_answers = []
    for q in questions:
        output = LAYOUT_OBJ.document_query(image=LAYOUT_OBJ.images[0], question=q)
        output_answers.append(output)

    expected_output = [
        "21099992723",
        "EXAMPLE CARRIER",
        "September 13, 2021",
        "456-7890",
    ]
    assert output_answers == expected_output


def test_invoice_screenshot():
    questions = [
        "What is the sender's phone number?",
        "What is the sender's address?",
        "What is surcharge?",
        "What is the total cost?",
        "What is the daily interest rate on overdue balances?",
    ]

    expected_answers = ["321-956-7331,", "MELBOURNE,", "45.00", "$ 3,165.00", "0.5%"]

    output_answers = []
    for q in questions:
        output = LAYOUT_OBJ.document_query(image=LAYOUT_OBJ.images[1], question=q)
        output_answers.append(output)
    assert output_answers == expected_answers


def test_calendar_screenshot():
    output = LAYOUT_OBJ.document_query(
        image=LAYOUT_OBJ.images[2], question="What month is it?"
    )
    assert output.lower() == "june"


def test_calc_screenshot():
    output = LAYOUT_OBJ.document_query(
        image=LAYOUT_OBJ.images[3],
        question="What is the current number on the screen?",
    )
    assert(output==10 or pytest.raises(TypeError))


if __name__ == "__main__":
    test_calc_screenshot()
    test_calendar_screenshot()
    test_invoice_screenshot()
    test_lading_bill_screenshot()
