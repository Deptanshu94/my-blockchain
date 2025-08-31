import json
import hashlib
import time
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Blockchain class
class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.load_data()
        if not self.chain:  
            self.create_block(previous_hash="0")  # Genesis block

    def load_data(self):
        # Load transactions and blockchain from transactions.json if it exists 
        try:
            with open("transactions.json", "r") as file:
                data = json.load(file)
                self.chain = data.get("chain", [])
                self.pending_transactions = data.get("pending_transactions", [])
        except (FileNotFoundError, json.JSONDecodeError):
            self.chain = []
            self.pending_transactions = []

    def save_data(self):
        # Save both blockchain and pending transactions to transactions.json 
        with open("transactions.json", "w") as file:
            json.dump({"chain": self.chain, "pending_transactions": self.pending_transactions}, file, indent=4)

    def create_block(self, previous_hash):
        # Mines a block, adds it to the chain, and moves transactions to history
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time.time(),
            "transactions": self.pending_transactions[:],  # Copy transactions into the block
            "previous_hash": previous_hash
        }
        block["hash"] = hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()
        self.chain.append(block)

        # Clear only pending transactions, keep mined ones stored
        self.pending_transactions = []
        self.save_data()
        return block

    def add_transaction(self, sender, receiver, amount):
        """ Adds a new transaction and saves it """
        transaction = {"sender": sender, "receiver": receiver, "amount": amount}
        self.pending_transactions.append(transaction)
        self.save_data()
        return transaction

# Initialize Blockchain
blockchain = Blockchain()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_transactions', methods=['GET'])
def get_transactions():
    """ Returns all pending transactions dynamically """
    return jsonify(blockchain.pending_transactions)

@app.route('/get_chain', methods=['GET'])
def get_chain():
    """ Returns the blockchain ledger dynamically """
    return jsonify(blockchain.chain)

@app.route('/submit', methods=['POST'])
def submit_transaction():
    data = request.json
    if "sender" in data and "receiver" in data and "amount" in data:
        blockchain.add_transaction(data["sender"], data["receiver"], data["amount"])
        return jsonify({"message": "Transaction submitted!"}), 200
    return jsonify({"error": "Invalid data"}), 400

@app.route('/mine', methods=['POST'])
def mine_block():
    if not blockchain.pending_transactions:
        return jsonify({"message": "No transactions to mine!"}), 400
    new_block = blockchain.create_block(blockchain.chain[-1]["hash"])
    return jsonify(new_block), 200

if __name__ == "__main__":
    app.run(debug=True)
