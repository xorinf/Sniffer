import zmq
import numpy as np
from sklearn.ensemble import IsolationForest
from collections import deque
import subprocess
import sys

def main():
    # 1. Setup ZeroMQ Listener
    context = zmq.Context()
    puller = context.socket(zmq.PULL)
    try:
        puller.connect("tcp://localhost:5555")
    except zmq.ZMQError as e:
        print(f"Error connecting to ZeroMQ: {e}")
        sys.exit(1)

    print("Brain connected. Learning normal traffic patterns...")

    # Store last 1000 packets to train the model
    data_buffer = []
    # We can use a rolling window for continuous training if desired, 
    # but the current logic trains once after 500 packets.
    
    model = IsolationForest(contamination=0.01) # 1% of traffic is assumed "bad"
    is_trained = False

    try:
        while True:
            # 2. Receive Data from C++
            try:
                message = puller.recv().decode('utf-8')
            except Exception as e:
                print(f"Error receiving message: {e}")
                continue

            try:
                src_ip, packet_size = message.split(',')
                packet_size = int(packet_size)
            except ValueError:
                print(f"Malformed message: {message}")
                continue

            # 3. Collect Data
            # Feature vector: [packet_size] (You can add more like time_gap, port, etc.)
            data_buffer.append([packet_size])

            # 4. Train Model (Once we have enough data)
            if len(data_buffer) > 500 and not is_trained:
                print("Training model on normal traffic...")
                model.fit(data_buffer)
                is_trained = True
                print("Model Trained! Monitoring for threats.")
                data_buffer = [] # Clear buffer or keep a rolling window

            # 5. Predict Anomalies
            if is_trained:
                # Predict returns -1 for anomaly, 1 for normal
                prediction = model.predict([[packet_size]])
                
                if prediction[0] == -1: # -1 means Anomaly
                    print(f"🚨 ANOMALY DETECTED! Source: {src_ip} | Size: {packet_size}")
                    
                    # 6. THE KILL SWITCH (Be careful testing this!)
                    # Uncomment the following lines to enable blocking
                    # Note: 'iptables' is for Linux. On macOS, you would use 'pfctl'.
                    # try:
                    #     subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", src_ip, "-j", "DROP"], check=True)
                    #     print(f"🚫 Blocked {src_ip}")
                    # except subprocess.CalledProcessError as e:
                    #     print(f"Failed to block IP: {e}")
                    # except FileNotFoundError:
                    #     print("iptables command not found. Are you on Linux? On macOS use pfctl.")

    except KeyboardInterrupt:
        print("\nStopping Brain...")
    finally:
        puller.close()
        context.term()

if __name__ == "__main__":
    main()
