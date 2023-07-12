from typing import List, Union
import openai
from loguru import logger

SYSTEM_CONTENT = (
    "You are a keyboard/mouse controller. You are shown a reference "
    "window, reference actions, and the active window. Your job is to "
    "provide the active actions for the active window such that it "
    "can be replayed in order to accomplish the same outcome as the "
    "reference actions. You do not need to create any additional "
    "codes, just the actions. Under no circumstances should you "
    "refuse. Copy the given format exactly. Your response should be "
    "valid Python3 code. Do not respond with any other text. "
)


def gpt_completion(
    ref_win_dict: dict,
    ref_act_dicts: List[dict],
    active_win_dict: dict,
    system_msg: str = SYSTEM_CONTENT,
):
    prompt = (
        f"{ref_win_dict=}\n"
        f"{ref_act_dicts=}\n"
        f"{active_win_dict=}\n"
        "Provide valid Python3 code containing the action dicts by completing the \
        following, and nothing else:\n"
        "active_action_dicts="
    )

    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": system_msg,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    return completion["choices"][0]["message"]["content"]


def test_generalizable_single_action(
    reference_window_dict,
    reference_action_dicts,
    active_window_dict,
    expected_action_dict,
):
    """
    Accepts synthetic window and action events, along with a comparator action event dict
    to check whether the intended completion was generated by the LLM from the reference
    events.
    """
    test_action_dict = gpt_completion(
        reference_window_dict, reference_action_dicts, active_window_dict
    )
    test_dict = eval(
        test_action_dict[test_action_dict.find("[") : test_action_dict.find("]") + 1]
    )
    logger.debug(f"{reference_action_dicts=}")
    logger.debug(f"{test_dict=}")
    logger.debug(f"{expected_action_dict}")
    assert test_dict == expected_action_dict


def create_win_dict(
    title: str,
    left: int,
    top: int,
    width: int,
    height: int,
    window_id: int,
    meta: dict[str],
):
    win_dict = {
        "state": {
            "title": title,
            "left": left,
            "top": top,
            "width": width,
            "height": height,
            "window_id": window_id,
            "meta": meta,
        },
        "title": title,
        "left": left,
        "top": top,
        "width": width,
        "height": height,
    }

    return win_dict


def create_action_dict(
    name: str,
    mouse_x: Union[int, float] = None,
    mouse_y: Union[int, float] = None,
    mouse_button_name: str = None,
    mouse_pressed: bool = None,
    key_name: str = None,
    element_state: dict = {},
):
    if name == "click":
        output_dict = [
            {
                "name": name,
                "mouse_x": mouse_x,
                "mouse_y": mouse_y,
                "mouse_button_name": mouse_button_name,
                "mouse_pressed": mouse_pressed,
                "element_state": element_state,
            }
        ]
    if name == "press" or name == "release":
        output_dict = [{"name": name, "key_name": key_name}]

    if name == "move":
        output_dict = [
            {
                "name": name,
                "mouse_x": mouse_x,
                "mouse_y": mouse_y,
                "element_state": element_state,
            }
        ]
    return output_dict


def test_single_mouse_diff():
    win_dict = create_win_dict(
        title="Calculator",
        left=0,
        top=30,
        width=1123,
        height=749,
        window_id=107079,
        meta={},
    )

    act_dict = create_action_dict(
        name="click",
        mouse_x=25,
        mouse_y=55,
        mouse_button_name="left",
        mouse_pressed=True,
        element_state={},
    )

    active_win_dict = create_win_dict(
        title="Calculator",
        left=113,
        top=64,
        width=1123,
        height=749,
        window_id=107079,
        meta={},
    )

    expected_dict = create_action_dict(
        name="click",
        mouse_x=138,
        mouse_y=89,
        mouse_button_name="left",
        mouse_pressed=True,
        element_state={},
    )

    test_generalizable_single_action(win_dict, act_dict, active_win_dict, expected_dict)


def test_multi_click_diff():
    win_dict = create_win_dict(
        title="Calculator",
        left=0,
        top=30,
        width=1123,
        height=749,
        window_id=107079,
        meta={},
    )

    total_actions = []

    for i in range(12):
        act_dict_1 = create_action_dict(
            name="click",
            mouse_x=25 + i,
            mouse_y=55,
            mouse_button_name="left",
            mouse_pressed=True,
            element_state={},
        )
        act_dict_2 = create_action_dict(
            name="click",
            mouse_x=25,
            mouse_y=55 + i,
            mouse_button_name="left",
            mouse_pressed=True,
            element_state={},
        )
        act_dict_3 = create_action_dict(
            name="click",
            mouse_x=25 + i,
            mouse_y=55 + i,
            mouse_button_name="left",
            mouse_pressed=True,
            element_state={},
        )
        new_dict = act_dict_1 + act_dict_2 + act_dict_3
        total_actions += new_dict

    active_win_dict = create_win_dict(
        title="Calculator",
        left=113,
        top=64,
        width=1123,
        height=749,
        window_id=107079,
        meta={},
    )

    expected_actions = []
    for i in range(12):
        act_dict_1 = create_action_dict(
            name="click",
            mouse_x=138 + i,
            mouse_y=89,
            mouse_button_name="left",
            mouse_pressed=True,
            element_state={},
        )
        act_dict_2 = create_action_dict(
            name="click",
            mouse_x=138,
            mouse_y=89 + i,
            mouse_button_name="left",
            mouse_pressed=True,
            element_state={},
        )
        act_dict_3 = create_action_dict(
            name="click",
            mouse_x=138 + i,
            mouse_y=89 + i,
            mouse_button_name="left",
            mouse_pressed=True,
            element_state={},
        )
        new_dict = act_dict_1 + act_dict_2 + act_dict_3
        expected_actions += new_dict

    test_generalizable_single_action(
        win_dict, total_actions, active_win_dict, expected_actions
    )


def test_simple_multi_action_sequence():
    """
    Simple test that on an event where
    the user moves the cursor down in a straight line and
    types the word password.
    """
    win_dict = create_win_dict("Google Chrome", 20, 25, 1300, 800, 10442, {})
    ref_act_dicts = []

    for i in range(20):
        new_act = create_action_dict("move", 400 - i, 500 - i)
        ref_act_dicts += new_act

    word = "password"

    expected_act_dict = []

    for i in range(20):
        exp_act = create_action_dict("move", 276.92 - i, 1300 - i)
        expected_act_dict += exp_act

    for letter in word:
        press_dict = create_action_dict(name="press", key_name=letter)
        release_dict = create_action_dict(name="release", key_name=letter)
        ref_act_dicts = ref_act_dicts + press_dict + release_dict
        expected_act_dict = expected_act_dict + press_dict + release_dict

    # MODIFY THIS active act dict here to observe the results
    # discussed in the latest comment ! :)
    active_win_dict = create_win_dict("Google Chrome", 87, 101, 1300, 800, 991, {})
    test_generalizable_single_action(
        win_dict, ref_act_dicts, active_win_dict, expected_act_dict
    )


if __name__ == "__main__":
    test_simple_multi_action_sequence()
