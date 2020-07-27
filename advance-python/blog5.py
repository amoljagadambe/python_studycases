from flask import Flask, render_template, url_for, flash, redirect, request, session
import flask
import mysql.connector
from datetime import datetime

db = mysql.connector.connect(
    host="127.0.0.1", user="18007746", password="tJjZvr82Aemexy6F", database="18007746")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hello'


@app.route("/")
@app.route("/topics")
def topics():
    topics = []
    cursor = db.cursor()
    cursor.execute(
        "SELECT registery3.username, title,content,date_posted, topicID FROM topics INNER JOIN registery3 ON "
        "topics.username=registery3.username ORDER BY date_posted DESC;")
    for title, content, date_posted, username, topicID in cursor:
        topics.append([title, content, date_posted, username, topicID])
    if 'user' in session:
        return render_template('loggedin_index.html', topics=topics)
    else:
        return render_template('index2.html', topics=topics)


@app.route("/login", methods=['POST'])
def login():
    if request.method == 'POST':
        username2 = request.form['luser']
        password2 = request.form['lpass']
        cursor1 = db.cursor()
        cursor1.execute("SELECT * FROM registery3 WHERE username = (%s) AND password = (%s)", (username2, password2))
        account = cursor1.fetchall()
        if account:
            flash('Logged in successfully!', "success")
            session['user'] = username2
            return redirect(url_for('loggedin'))
        else:
            flash("Account Invalid", "error")
            return redirect(url_for('topics'))


@app.route("/register", methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form['ruser']
        password = request.form['rpass']
        cursor = db.cursor()
        cursor.execute("SELECT * FROM registery3 WHERE username = (%s) ", (username,))
        account = cursor.fetchall()
        if account:
            flash('Registration Failed! Username Already Exists! Choose Another one', "error")
            topics = []
            cursor = db.cursor()
            cursor.execute(
                "SELECT registery3.username, title,content,date_posted, topicID FROM topics INNER JOIN registery3 ON "
                "topics.username=registery3.username ORDER BY date_posted DESC;")
            for title, content, date_posted, username, topicID in cursor:
                topics.append([title, content, date_posted, username, topicID])
            return render_template('index2.html', topics=topics)
        else:
            cursor.execute("INSERT INTO registery3(username,password) VALUES (%s,%s) ", (username, password))
            db.commit()

            flash('Successfully Registered! Now Log In', "success")
            topics = []
            cursor = db.cursor()
            cursor.execute(
                "SELECT registery3.username, title,content,date_posted, topicID FROM topics INNER JOIN registery3 ON "
                "topics.username=registery3.username ORDER BY date_posted DESC;")
            for title, content, date_posted, username, topicID in cursor:
                topics.append([title, content, date_posted, username, topicID])
            cursor.close()
            return render_template('index2.html', topics=topics)
    return render_template('index2.html')


@app.route("/claims/<int:topicid>", methods=["POST", "GET"])
def claims(topicid):
    if 'user' in session:
        claims = []
        cursor = db.cursor()
        cursor.execute(
            "SELECT registery3.username, claims.title,claims.content,claims.date_posted,related_claim_id,relation, "
            "claims.topicID,claimID FROM ((claims INNER JOIN topics ON claims.topicID=topics.topicID) INNER JOIN "
            "registery3 ON claims.username=registery3.username) WHERE claims.topicID=(%s)  ORDER BY date_posted DESC",
            (topicid,))
        for title, content, date_posted, username, topicID, claimID, relation, related_claim_id in cursor:
            claims.append([title, content, date_posted, username, topicID, claimID, relation, related_claim_id])
        session['my_list'] = claims
        return render_template('loggedin_claims.html', claims=claims)
    else:
        claims = []
        cursor = db.cursor()
        cursor.execute(
            "SELECT registery3.username, claims.title,claims.content,claims.date_posted,related_claim_id,relation, "
            "claims.topicID,claimID FROM ((claims INNER JOIN topics ON claims.topicID=topics.topicID) INNER JOIN "
            "registery3 ON claims.username=registery3.username) WHERE claims.topicID=(%s) ORDER BY date_posted DESC",
            (topicid,))
        for title, content, date_posted, username, topicID, claimID, relation, related_claim_id in cursor:
            claims.append([title, content, date_posted, username, topicID, claimID, relation, related_claim_id])
        session['my_list'] = claims
        return render_template('claims2.html', claims=claims)


@app.route("/replies/<int:claimid>", methods=["POST", "GET"])
def replies(claimid):
    if 'user' in session:
        claim = []
        topicid = []
        replies = []
        cursor = db.cursor()
        cursor.execute(
            "SELECT registery3.username, claims.title,claims.content,claims.date_posted,related_claim_id,relation, "
            "claims.topicID,claimID FROM ((claims INNER JOIN topics ON claims.topicID=topics.topicID) INNER JOIN "
            "registery3 ON claims.username=registery3.username) WHERE claims.claimID =(%s)  ORDER BY date_posted DESC",
            (claimid,))
        for title, content, date_posted, username, topicID, claimID, relation, related_claim_id in cursor:
            claim.append([title, content, date_posted, username, topicID, claimID, relation, related_claim_id])
            topicid.append([topicID])

        cursor.execute(
            "SELECT registery3.username, replies.title,replies.content,replies.date_posted,related_reply_id,"
            "relation1,relation2, replies.claimID,replyID FROM ((replies INNER JOIN claims ON "
            "replies.claimID=claims.claimID) INNER JOIN registery3 ON replies.username=registery3.username) WHERE "
            "replies.claimID=(%s)  ORDER BY date_posted DESC",
            (claimid,))
        for username, title, content, date_posted, related_reply_id, relation1, relation2, claimID, replyID in cursor:
            replies.append(
                [username, title, content, date_posted, related_reply_id, relation1, relation2, claimID, replyID])

        session['my_list2'] = replies
        session['my_list3'] = claim
        session['my_list4'] = topicid
        return render_template('loggedin_replies.html', replies=replies)
    else:
        claim = []
        replies = []
        topicid = []
        cursor = db.cursor()
        cursor.execute(
            "SELECT registery3.username, claims.title,claims.content,claims.date_posted,related_claim_id,relation, "
            "claims.topicID,claimID FROM ((claims INNER JOIN topics ON claims.topicID=topics.topicID) INNER JOIN "
            "registery3 ON claims.username=registery3.username) WHERE claims.claimID=(%s)  ORDER BY date_posted DESC",
            (claimid,))
        for title, content, date_posted, username, topicID, claimID, relation, related_claim_id in cursor:
            claim.append([title, content, date_posted, username, topicID, claimID, relation, related_claim_id])
            topicid.append([topicID])

        cursor.execute(
            "SELECT registery3.username, replies.title,replies.content,replies.date_posted,related_reply_id,"
            "relation1,relation2, replies.claimID,replyID FROM ((replies INNER JOIN claims ON "
            "replies.claimID=claims.claimID) INNER JOIN registery3 ON replies.username=registery3.username) WHERE "
            "replies.claimID=(%s)  ORDER BY date_posted DESC",
            (claimid,))
        for username, title, content, date_posted, related_reply_id, relation1, relation2, claimID, replyID in cursor:
            replies.append(
                [username, title, content, date_posted, related_reply_id, relation1, relation2, claimID, replyID])

        session['my_list2'] = replies
        session['my_list3'] = claim
        session['my_list4'] = topicid
        return render_template('replies2.html', replies=replies)


@app.route("/loggedin", methods=["POST", "GET"])
def loggedin():
    if 'user' in session:
        return redirect(url_for('topics'))
    else:
        flash('You are not allowed to view this page without logging in!', "error")
        return render_template('error.html')


@app.route("/loggedin_claims", methods=["POST", "GET"])
def loggedin_claims():
    if 'user' in session:
        return render_template('loggedin_claims.html', claims=claims)
    else:
        flash('You are not allowed to view this page without logging in!', "error")
        return render_template('error.html')


@app.route("/claims2", methods=["POST", "GET"])
def claims2():
    return render_template('claims2.html', claims=claims)


@app.route("/loggedin_replies", methods=["POST", "GET"])
def loggedin_replies():
    if 'user' in session:
        return render_template('loggedin_replies.html')
    else:
        flash('You are not allowed to view this page without logging in!', "error")
        return render_template('error.html')


@app.route("/replies2", methods=["POST", "GET"])
def replies2():
    return render_template('replies2.html', replies=replies)


@app.route("/createtopic", methods=["POST", "GET"])
def createtopic():
    if 'user' in session:
        return render_template('create_topic.html')
    else:
        flash('You are not allowed to view this page without logging in!', "error")
        return render_template('error.html')


@app.route("/createclaim", methods=["POST", "GET"])
def createclaim():
    if 'user' in session:
        return render_template('create_claim.html')
    else:
        flash('You are not allowed to view this page without logging in!', "error")
        return render_template('error.html')


@app.route("/createreply", methods=["POST", "GET"])
def createreply():
    if 'user' in session:
        return render_template('create_reply.html')
    else:
        flash('You are not allowed to view this page without logging in!', "error")
        return render_template('error.html')


@app.route("/logout", methods=["POST", "GET"])
def logout():
    if 'user' in session:
        session.pop('user')
        flash('You have been logged out!', "success")
    return redirect(url_for('topics'))


@app.route("/createtopic2", methods=["POST", "GET"])
def createtopic2():
    if request.method == 'POST':
        if 'user' in session:
            username = session['user']
            title = request.form['fname']
            content = request.form['message']
            dateposted = datetime.now()
            cursor = db.cursor()
            cursor.execute("INSERT INTO topics(title,content,date_posted,username) VALUES (%s,%s,%s,%s) ",
                           (title, content, dateposted, username))
            db.commit()
            cursor.close()
            return redirect(url_for('topics'))


@app.route("/createclaim2", methods=["POST", "GET"])
def createclaim2():
    if request.method == 'POST':
        if 'user' in session:
            username = session['user']
            title = request.form['title']
            content = request.form['content']
            topicid = request.form['topicid']
            relation1 = request.form['gender']
            claimid = request.form['claimid']
            dateposted = datetime.now()
            cursor = db.cursor()
            if relation1 == 'yes':
                relation2 = request.form['gender1']
                cursor.execute("SELECT * FROM claims WHERE claimID = (%s)", (claimid,))
                match = cursor.fetchall()
                if match:
                    cursor.execute(
                        "INSERT INTO claims(title,content,date_posted,topicID,related_claim_id,relation,username) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s) ",
                        (title, content, dateposted, topicid, claimid, relation2, username))
                    db.commit()
                    cursor.close()
                    return redirect(url_for('claims', topicid=topicid))
                else:
                    cursor.execute(
                        "INSERT INTO claims(title,content,date_posted,topicID,username) VALUES (%s,%s,%s,%s,%s) ",
                        (title, content, dateposted, topicid, username))
                    db.commit()
                    cursor.close()
                    return redirect(url_for('claims', topicid=topicid))
            else:
                cursor.execute(
                    "INSERT INTO claims(title,content,date_posted,topicID,username) VALUES (%s,%s,%s,%s,%s) ",
                    (title, content, dateposted, topicid, username))
                db.commit()
                cursor.close()
                return redirect(url_for('claims', topicid=topicid))


@app.route("/createreply2", methods=["POST", "GET"])
def createreply2():
    if request.method == 'POST':
        if 'user' in session:
            username = session['user']
            title = request.form['title']
            content = request.form['content']
            relation1 = request.form['gender']
            claimid = request.form['claimid']
            claimid2 = request.form['claimid2']
            replyid = request.form['replyid']
            relation2 = request.form['gender1']
            dateposted = datetime.now()
            cursor = db.cursor()
            if relation1 == 'yes':
                cursor.execute("SELECT * FROM claims WHERE claimID = (%s)", (claimid,))
                match = cursor.fetchall()
                if match:
                    cursor.execute(
                        "INSERT INTO replies(title,content,date_posted,claimID,relation1,username) VALUES (%s,%s,%s,"
                        "%s,%s,%s) ",
                        (title, content, dateposted, claimid, relation2, username))
                    db.commit()
                    cursor.close()
                    return redirect(url_for('replies', claimid=claimid))
                else:
                    cursor.execute("INSERT INTO replies(title,content,date_posted,username) VALUES (%s,%s,%s,%s) ",
                                   (title, content, dateposted, username))
                    db.commit()
                    cursor.close()
                    return redirect(url_for('replies', claimid=claimid))

            if relation1 == 'no':
                cursor.execute(
                    "SELECT * FROM replies INNER JOIN claims ON replies.claimID=claims.claimID  WHERE "
                    "replies.claimID=(%s)  AND replies.replyID=(%s) ORDER BY replies.date_posted DESC",
                    (claimid2, replyid))
                match = cursor.fetchall()
                if match:
                    cursor.execute(
                        "INSERT INTO replies(title,content,date_posted,claimID,related_reply_id,relation2,username) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s) ",
                        (title, content, dateposted, claimid2, replyid, relation2, username))
                    db.commit()
                    cursor.close()
                    return redirect(url_for('replies', claimid=claimid2))
                else:
                    cursor.execute("INSERT INTO replies(title,content,date_posted,username) VALUES (%s,%s,%s,%s) ",
                                   (title, content, dateposted, username))
                    db.commit()
                    cursor.close()
                    return redirect(url_for('replies', claimid=claimid2))


if __name__ == '__main__':
    app.run(debug=True)
