from flask import Flask, render_template, session, redirect, url_for
import random

app = Flask(__name__)
app.secret_key = "klucz"


@app.route('/')
def select_mode():  # put application's code here
    return render_template('index.html')


@app.route('/begin/<int:mode>')
def begin(mode):
    session["mode"] = mode
    session["turn"] = 1

    session["board"] = []
    board = session["board"]
    for i in range(100):
        board.append(i)
    board[0] = ["x1", "x2", "y1", "y2"]

    session["player_positions"] = {
        "x1": 0,
        "x2": 0,
        "y1": 0,
        "y2": 0
    }
    session["active_piece"] = "x1"

    session["snakes_ladders"] = {}
    n = random.sample(range(1, 99), 20)
    i = 0
    while i < len(n):
        session["snakes_ladders"][n[i]] = n[i + 1]
        i += 2

    return render_template('begin.html')


@app.route('/select_piece')
def select_piece():
    session["board"] = session.get("board", [])
    session["player_positions"] = session.get("player_positions")
    session["snakes_ladders"] = session.get("snakes_ladders")

    a = random.randint(1, 6)
    b = random.randint(1, 6)
    session["dice"] = [a, b, a + b]
    return render_template('select_piece.html')


@app.route('/move_piece/<active>')
def move_piece(active):
    session["board"] = session.get("board", [])
    session["player_positions"] = session.get("player_positions")
    session["snakes_ladders"] = session.get("snakes_ladders")

    if active == "x1" or active == "x2":
        session["active_piece"] = active
        session["moves_to"] = [session["player_positions"][active] + session["dice"][0], session["player_positions"][active] + session["dice"][1], session["player_positions"][active] + session["dice"][2]]
    return render_template('move_piece.html')


@app.route('/moving/<int:move>')
def moving(move):
    session["board"] = session.get("board", [])
    session["player_positions"] = session.get("player_positions")
    session["snakes_ladders"] = session.get("snakes_ladders")

    if move in session["moves_to"]:
        x1 = session["player_positions"]["x1"]
        x2 = session["player_positions"]["x2"]
        y1 = session["player_positions"]["y1"]
        y2 = session["player_positions"]["y2"]

        if session["active_piece"] == "x1":
            if move == session["moves_to"][2]:
                session["board"][x1] = x1
                x1 = move
            elif move == session["moves_to"][0]:
                session["board"][x1] = x1
                x1 = move
                session["board"][x2] = x2
                x2 += session["dice"][1]
            elif move == session["moves_to"][1]:
                session["board"][x1] = x1
                x1 = move
                session["board"][x2] = x2
                x2 += session["dice"][0]

        if session["active_piece"] == "x2":
            if move == session["moves_to"][2]:
                session["board"][x2] = x2
                x2 = move
            elif move == session["moves_to"][0]:
                session["board"][x2] = x2
                x2 = move
                session["board"][x1] = x1
                x1 += session["dice"][1]
            elif move == session["moves_to"][1]:
                session["board"][x2] = x2
                x2 = move
                session["board"][x1] = x1
                x1 += session["dice"][0]

        if str(x1) in session["snakes_ladders"]:
            x1 = session["snakes_ladders"][str(x1)]
        if str(x2) in session["snakes_ladders"]:
            x2 = session["snakes_ladders"][str(x2)]

        #przeskakiwanie o jeden pionek do przodu
        if x1 == x2 and session["active_piece"] == "x1":
            x1 += 1
        elif x1 == x2 and session["active_piece"] == "x2":
            x2 += 1

        #zbijanie
        if (x1 == y1 or x2 == y1) and y1 != 99:
            session["board"][y1] = y1
            y1 = 0
        if (x1 == y2 or x2 == y2) and y2 != 99:
            session["board"][y2] = y2
            y2 = 0

        #meta
        if x1 > 99:
            x1 = 99
        if x2 > 99:
            x2 = 99
        if x1 == 99 and x2 == 99:
            session["winner"] = 1
            return redirect(url_for('end_game'))

        session["player_positions"]["x1"] = x1
        session["player_positions"]["x2"] = x2
        session["player_positions"]["y1"] = y1
        session["player_positions"]["y2"] = y2

        session["board"][x1] = "x1"
        session["board"][x2] = "x2"
        session["board"][y1] = "y1"
        session["board"][y2] = "y2"

        #pierwsze pole
        if y1 == y2 and y1 == 0:
            session["board"][y1] = ["y1", "y2"]
        if x1 == y1 and x1 == y2 and x1 == 0:
            session["board"][x1] = ["x1", "y1", "y2"]
        if x2 == y1 and x2 == y2 and x2 == 0:
            session["board"][x2] = ["x2", "y1", "y2"]

    return render_template('moving.html')


@app.route('/ai_move')
def ai_move():
    session["board"] = session.get("board", [])
    session["player_positions"] = session.get("player_positions")
    session["snakes_ladders"] = session.get("snakes_ladders")

    x1 = session["player_positions"]["x1"]
    x2 = session["player_positions"]["x2"]
    y1 = session["player_positions"]["y1"]
    y2 = session["player_positions"]["y2"]
    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    session["enemy_dice"] = [d1, d2]

    if y1 == 99:
        session["board"][y2] = y2
        y2 += d1 + d2
    elif y2 == 99:
        session["board"][y1] = y1
        y1 += d1 + d2
    elif y1 >= y2:
        if d1 >= d2:
            session["board"][y1] = y1
            y1 += d1
            session["board"][y2] = y2
            y2 += d2
        else:
            session["board"][y1] = y1
            y1 += d2
            session["board"][y2] = y2
            y2 += d1
    else:
        if d1 >= d2:
            session["board"][y2] = y2
            y2 += d1
            session["board"][y1] = y1
            y1 += d2
        else:
            session["board"][y2] = y2
            y2 += d2
            session["board"][y1] = y1
            y1 += d1

    # stawanie na wężu lub drabinie
    if str(y1) in session["snakes_ladders"]:
        y1 = session["snakes_ladders"][str(y1)]
    if str(y2) in session["snakes_ladders"]:
        y2 = session["snakes_ladders"][str(y2)]

    # przeskakiwanie o jeden pionek do przodu
    if y1 == y2 and session["active_piece"] == "y1":
        y1 += 1
    elif y1 == y2 and session["active_piece"] == "y2":
        y2 += 1

    # zbijanie
    if (y1 == x1 or y2 == x1) and x1 != 99:
        session["board"][x1] = x1
        x1 = 0
    if (y1 == x2 or y2 == x2) and x2 != 99:
        session["board"][x2] = x2
        x2 = 0

    # meta
    if y1 > 99:
        y1 = 99
    if y2 > 99:
        y2 = 99
    if y1 == 99 and y2 == 99:
        session["winner"] = 2
        return redirect(url_for('end_game'))

    session["player_positions"]["x1"] = x1
    session["player_positions"]["x2"] = x2
    session["player_positions"]["y1"] = y1
    session["player_positions"]["y2"] = y2

    session["board"][x1] = "x1"
    session["board"][x2] = "x2"
    session["board"][y1] = "y1"
    session["board"][y2] = "y2"

    # pierwsze pole
    if x1 == x2 and x1 == 0:
        session["board"][x1] = ["x1", "x2"]
    if y1 == y2 and y1 == 0:
        session["board"][y1] = ["y1", "y2"]

    return render_template('ai_move.html')


@app.route('/end_game')
def end_game():
    session["board"] = session.get("board", [])
    session["winner"] = session.get("winner")
    session["mode"] = session.get("mode")

    return render_template('end_game.html')


# Gracz vs gracz

@app.route('/select_piece2')
def select_piece2():
    session["board"] = session.get("board", [])
    session["player_positions"] = session.get("player_positions")
    session["snakes_ladders"] = session.get("snakes_ladders")
    session["mode"] = session.get("mode")
    session["turn"] = session.get("turn")

    a = random.randint(1, 6)
    b = random.randint(1, 6)
    session["dice"] = [a, b, a + b]
    return render_template('select_piece2.html')


@app.route('/move_piece2/<active>')
def move_piece2(active):
    session["board"] = session.get("board", [])
    session["player_positions"] = session.get("player_positions")
    session["snakes_ladders"] = session.get("snakes_ladders")
    session["mode"] = session.get("mode")
    session["turn"] = session.get("turn")

    if active == "x1" or active == "x2" or active == "y1" or active == "y2":
        session["active_piece"] = active
        session["moves_to"] = [session["player_positions"][active] + session["dice"][0], session["player_positions"][active] + session["dice"][1], session["player_positions"][active] + session["dice"][2]]
    return render_template('move_piece2.html')


@app.route('/moving2/<int:move>')
def moving2(move):
    session["board"] = session.get("board", [])
    session["player_positions"] = session.get("player_positions")
    session["snakes_ladders"] = session.get("snakes_ladders")
    session["mode"] = session.get("mode")
    session["turn"] = session.get("turn")

    if move in session["moves_to"]:
        x1 = session["player_positions"]["x1"]
        x2 = session["player_positions"]["x2"]
        y1 = session["player_positions"]["y1"]
        y2 = session["player_positions"]["y2"]

        if session["active_piece"] == "x1":
            if move == session["moves_to"][2]:
                session["board"][x1] = x1
                x1 = move
            elif move == session["moves_to"][0]:
                session["board"][x1] = x1
                x1 = move
                session["board"][x2] = x2
                x2 += session["dice"][1]
            elif move == session["moves_to"][1]:
                session["board"][x1] = x1
                x1 = move
                session["board"][x2] = x2
                x2 += session["dice"][0]

        if session["active_piece"] == "x2":
            if move == session["moves_to"][2]:
                session["board"][x2] = x2
                x2 = move
            elif move == session["moves_to"][0]:
                session["board"][x2] = x2
                x2 = move
                session["board"][x1] = x1
                x1 += session["dice"][1]
            elif move == session["moves_to"][1]:
                session["board"][x2] = x2
                x2 = move
                session["board"][x1] = x1
                x1 += session["dice"][0]

        if session["active_piece"] == "y1":
            if move == session["moves_to"][2]:
                session["board"][y1] = y1
                y1 = move
            elif move == session["moves_to"][0]:
                session["board"][y1] = y1
                y1 = move
                session["board"][y2] = y2
                y2 += session["dice"][1]
            elif move == session["moves_to"][1]:
                session["board"][y1] = y1
                y1 = move
                session["board"][y2] = y2
                y2 += session["dice"][0]

        if session["active_piece"] == "y2":
            if move == session["moves_to"][2]:
                session["board"][y2] = y2
                y2 = move
            elif move == session["moves_to"][0]:
                session["board"][y2] = y2
                y2 = move
                session["board"][y1] = y1
                y1 += session["dice"][1]
            elif move == session["moves_to"][1]:
                session["board"][y2] = y2
                y2 = move
                session["board"][y1] = y1
                y1 += session["dice"][0]

        if str(x1) in session["snakes_ladders"]:
            x1 = session["snakes_ladders"][str(x1)]
        if str(x2) in session["snakes_ladders"]:
            x2 = session["snakes_ladders"][str(x2)]
        if str(y1) in session["snakes_ladders"]:
            y1 = session["snakes_ladders"][str(y1)]
        if str(y2) in session["snakes_ladders"]:
            y2 = session["snakes_ladders"][str(y2)]

        # przeskakiwanie o jeden pionek do przodu
        if x1 == x2 and session["active_piece"] == "x1":
            x1 += 1
        elif x1 == x2 and session["active_piece"] == "x2":
            x2 += 1
        if y1 == y2 and session["active_piece"] == "y1":
            y1 += 1
        elif y1 == y2 and session["active_piece"] == "y2":
            y2 += 1

        # zbijanie
        if session["turn"] == 1:
            if (x1 == y1 or x2 == y1) and y1 != 99:
                session["board"][y1] = y1
                y1 = 0
            if (x1 == y2 or x2 == y2) and y2 != 99:
                session["board"][y2] = y2
                y2 = 0
        if session["turn"] == 2:
            if (y1 == x1 or y2 == x1) and x1 != 99:
                session["board"][x1] = x1
                x1 = 0
            if (y1 == x2 or y2 == x2) and x2 != 99:
                session["board"][x2] = x2
                x2 = 0

        # meta
        if x1 > 99:
            x1 = 99
        if x2 > 99:
            x2 = 99
        if x1 == 99 and x2 == 99:
            session["winner"] = 1
            return redirect(url_for('end_game'))
        if y1 > 99:
            y1 = 99
        if y2 > 99:
            y2 = 99
        if y1 == 99 and y2 == 99:
            session["winner"] = 2
            return redirect(url_for('end_game'))

        session["player_positions"]["x1"] = x1
        session["player_positions"]["x2"] = x2
        session["player_positions"]["y1"] = y1
        session["player_positions"]["y2"] = y2

        session["board"][x1] = "x1"
        session["board"][x2] = "x2"
        session["board"][y1] = "y1"
        session["board"][y2] = "y2"

        if session["turn"] == 1:
            session["turn"] = 2
        elif session["turn"] == 2:
            session["turn"] = 1

    return render_template('moving2.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12139, debug=True)
