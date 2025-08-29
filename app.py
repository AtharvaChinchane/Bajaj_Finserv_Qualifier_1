# app.py
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Put your own values in environment variables before deploying (or change defaults)
FULL_NAME = os.getenv("FULL_NAME", "john doe")       # e.g. "John Doe" -> becomes "john_doe"
DOB = os.getenv("DOB", "17091999")                   # ddmmyyyy format, e.g. "17091999"
EMAIL = os.getenv("EMAIL", "john@xyz.com")
ROLL_NUMBER = os.getenv("ROLL_NUMBER", "ABCD123")

def make_user_id(full_name, dob):
    name = full_name.strip().lower().replace(" ", "_")
    return f"{name}_{dob}"

def _is_integer_string(s):
    return isinstance(s, int) or (isinstance(s, str) and s.lstrip("-").isdigit())

@app.route("/bfhl", methods=["POST"])
def bfhl():
    try:
        payload = request.get_json(force=True)
        if not payload or "data" not in payload:
            return jsonify({"is_success": False, "error": "Request must contain 'data' list"}), 400

        arr = payload["data"]
        if not isinstance(arr, list):
            return jsonify({"is_success": False, "error": "'data' must be a list"}), 400

        even_numbers = []
        odd_numbers = []
        alphabets = []
        special_characters = []
        char_list = []   # flattened alphabetic characters (preserve original case)
        total = 0

        for token in arr:
            # numeric types (JSON may give ints/floats)
            if isinstance(token, (int, float)):
                num = int(token)
                total += num
                s = str(num)
                if num % 2 == 0:
                    even_numbers.append(s)
                else:
                    odd_numbers.append(s)

            elif isinstance(token, str):
                # pure-digit string => number
                if token.isdigit():
                    num = int(token)
                    total += num
                    s = str(num)
                    if num % 2 == 0:
                        even_numbers.append(s)
                    else:
                        odd_numbers.append(s)

                # pure alphabetic string => treat as an alphabet token
                elif token.isalpha():
                    alphabets.append(token.upper())
                    # preserve each char in original case for concat_string logic
                    char_list.extend(list(token))

                else:
                    # mixed or special: collect non-alphanumeric characters as special characters
                    # also collect alphabetic characters inside mixed tokens for concat_string
                    for ch in token:
                        if not ch.isalnum():
                            special_characters.append(ch)
                        else:
                            if ch.isalpha():
                                char_list.append(ch)
                            elif ch.isdigit():
                                # digits embedded in mixed token — we add to total and parity lists as separate digits
                                num = int(ch)
                                total += num
                                if num % 2 == 0:
                                    even_numbers.append(str(num))
                                else:
                                    odd_numbers.append(str(num))
            else:
                # other types (rare) - stringify and classify char-by-char
                s = str(token)
                for ch in s:
                    if not ch.isalnum():
                        special_characters.append(ch)
                    elif ch.isalpha():
                        char_list.append(ch)
                    elif ch.isdigit():
                        num = int(ch)
                        total += num
                        if num % 2 == 0:
                            even_numbers.append(str(num))
                        else:
                            odd_numbers.append(str(num))

        # build concat_string:
        rev = char_list[::-1]
        out_chars = []
        for i, ch in enumerate(rev):
            if i % 2 == 0:
                out_chars.append(ch.upper())
            else:
                out_chars.append(ch.lower())
        concat_string = "".join(out_chars)

        response = {
            "is_success": True,
            "user_id": make_user_id(FULL_NAME, DOB),
            "email": EMAIL,
            "roll_number": ROLL_NUMBER,
            "odd_numbers": odd_numbers,
            "even_numbers": even_numbers,
            "alphabets": alphabets,
            "special_characters": special_characters,
            "sum": str(total),
            "concat_string": concat_string
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"is_success": False, "error": str(e)}), 500
@app.route("/", methods=["GET"])
def home():
    return {
        "message": "API is running ✅. Use POST /bfhl with JSON payload."
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

