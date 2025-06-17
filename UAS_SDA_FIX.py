import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import io
from graphviz import Digraph

class DecisionNode:
    def __init__(self, feature=None, threshold=None, left=None, right=None, prediction=None):
        self.feature = feature
        self.threshold = threshold
        self.left = left
        self.right = right
        self.prediction = prediction

class SleepDisorderTree:
    def __init__(self):
        self.root = self._build_tree()

    def _build_tree(self):
        insomnia_leaf = DecisionNode(prediction="Insomnia")
        sleep_apnea_leaf = DecisionNode(prediction="Sleep Apnea")
        none_leaf = DecisionNode(prediction="None")

        bmi_heart_node = DecisionNode(
            feature="bmi",
            threshold=25,
            left=sleep_apnea_leaf,
            right=DecisionNode(
                feature="heart_rate",
                threshold=80,
                left=none_leaf,
                right=insomnia_leaf
            )
        )

        steps_node = DecisionNode(
            feature="daily_steps",
            threshold=5300,
            left=none_leaf,
            right=bmi_heart_node
        )

        heart_node = DecisionNode(
            feature="heart_rate",
            threshold=76,
            left=sleep_apnea_leaf,
            right=insomnia_leaf
        )

        root = DecisionNode(
            feature="sleep_duration",
            threshold=7.3,
            left=heart_node,
            right=steps_node
        )

        return root

    def predict(self, features):
        return self._predict_node(self.root, features)

    def _predict_node(self, node, features):
        if node.prediction is not None:
            return node.prediction

        feature_value = features[node.feature]
        if feature_value <= node.threshold:
            return self._predict_node(node.left, features)
        else:
            return self._predict_node(node.right, features)

    def get_decision_path(self, features):
        path = []
        self._get_path(self.root, features, path)
        return path

    def _get_path(self, node, features, path):
        if node.prediction is not None:
            path.append(f"Prediksi: {node.prediction}")
            return

        feature_value = features[node.feature]
        condition = f"{node.feature} <= {node.threshold}"

        if feature_value <= node.threshold:
            path.append(f"{condition} = True ({feature_value} <= {node.threshold})")
            self._get_path(node.left, features, path)
        else:
            path.append(f"{condition} = False ({feature_value} > {node.threshold})")
            self._get_path(node.right, features, path)

def visualize_tree_graphviz(node, dot=None, counter=[0]):
    if dot is None:
        dot = Digraph()
    node_id = str(counter[0])
    counter[0] += 1

    if node.prediction:
        dot.node(node_id, f"Hasil: {node.prediction}", shape="box", style="filled", fillcolor="lightblue")
        return dot, node_id

    dot.node(node_id, f"{node.feature} <= {node.threshold}")
    dot_yes, yes_id = visualize_tree_graphviz(node.left, dot, counter)
    dot_no, no_id = visualize_tree_graphviz(node.right, dot, counter)

    dot.edge(node_id, yes_id, label="ya")
    dot.edge(node_id, no_id, label="tidak")
    return dot, node_id

class SimpleSleepPredictor:
    def __init__(self):
        self.rules = {
            'sleep_duration': {
                'threshold': 7.3,
                'left': {
                    'heart_rate': {
                        'threshold': 76,
                        'left': 'Sleep Apnea',
                        'right': 'Insomnia'
                    }
                },
                'right': {
                    'daily_steps': {
                        'threshold': 5300,
                        'left': 'None',
                        'right': {
                            'bmi': {
                                'threshold': 25,
                                'left': {
                                    'heart_rate': {
                                        'threshold': 80,
                                        'left': 'None',
                                        'right': 'Insomnia'
                                    }
                                },
                                'right': 'Sleep Apnea'
                            }
                        }
                    }
                }
            }
        }

    def predict(self, features):
        return self._predict_recursive(self.rules['sleep_duration'], features)

    def _predict_recursive(self, rule, features):
        if isinstance(rule, str):
            return rule

        feature = list(rule.keys())[0]
        threshold = rule[feature]['threshold']
        feature_value = features[feature]

        if feature_value <= threshold:
            return self._predict_recursive(rule[feature]['left'], features)
        else:
            return self._predict_recursive(rule[feature]['right'], features)

class SleepDisorderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sleep Disorder Prediction - Decision Tree")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')

        self.tree_predictor = SleepDisorderTree()
        self.simple_predictor = SimpleSleepPredictor()

        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(self.root, text="Sleep Disorder Prediction", font=('Arial', 20, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=20)

        input_frame = tk.Frame(self.root, bg='#f0f0f0')
        input_frame.pack(pady=20)

        tk.Label(input_frame, text="Durasi Tidur (jam):", font=('Arial', 12), bg='#f0f0f0').grid(row=0, column=0, sticky='e', padx=10, pady=5)
        self.sleep_entry = tk.Entry(input_frame, font=('Arial', 12), width=15)
        self.sleep_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(input_frame, text="Detak Jantung (BPM):", font=('Arial', 12), bg='#f0f0f0').grid(row=1, column=0, sticky='e', padx=10, pady=5)
        self.heart_entry = tk.Entry(input_frame, font=('Arial', 12), width=15)
        self.heart_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(input_frame, text="Jumlah Langkah Harian:", font=('Arial', 12), bg='#f0f0f0').grid(row=2, column=0, sticky='e', padx=10, pady=5)
        self.steps_entry = tk.Entry(input_frame, font=('Arial', 12), width=15)
        self.steps_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(input_frame, text="BMI:", font=('Arial', 12), bg='#f0f0f0').grid(row=3, column=0, sticky='e', padx=10, pady=5)
        self.bmi_entry = tk.Entry(input_frame, font=('Arial', 12), width=15)
        self.bmi_entry.grid(row=3, column=1, padx=10, pady=5)

        self.predict_btn = tk.Button(self.root, text="Prediksi", command=self.predict, font=('Arial', 14, 'bold'), bg='#3498db', fg='white', padx=30, pady=10)
        self.predict_btn.pack(pady=10)

        self.show_tree_btn = tk.Button(self.root, text="Tampilkan Pohon Keputusan", command=self.show_decision_tree, font=('Arial', 12), bg='#27ae60', fg='white')
        self.show_tree_btn.pack(pady=10)

        self.result_label = tk.Label(self.root, text="", font=('Arial', 16, 'bold'), bg='#f0f0f0', fg='#e74c3c')
        self.result_label.pack(pady=10)

        path_frame = tk.Frame(self.root, bg='#f0f0f0')
        path_frame.pack(pady=20, fill='both', expand=True)

        tk.Label(path_frame, text="Jalur Keputusan:", font=('Arial', 14, 'bold'), bg='#f0f0f0').pack()

        self.path_text = tk.Text(path_frame, height=15, width=80, font=('Courier', 10), bg='#ecf0f1', fg='#2c3e50')
        scrollbar = tk.Scrollbar(path_frame, orient="vertical", command=self.path_text.yview)
        self.path_text.configure(yscrollcommand=scrollbar.set)

        self.path_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def predict(self):
        try:
            features = {
                'sleep_duration': float(self.sleep_entry.get()),
                'heart_rate': float(self.heart_entry.get()),
                'daily_steps': float(self.steps_entry.get()),
                'bmi': float(self.bmi_entry.get())
            }

            if any(v < 0 for v in features.values()):
                raise ValueError("Nilai tidak boleh negatif")

            result = self.tree_predictor.predict(features)
            self.result_label.config(text=f"Hasil Prediksi: {result}")
            path = self.tree_predictor.get_decision_path(features)

            self.path_text.delete(1.0, tk.END)
            self.path_text.insert(tk.END, "INPUT FEATURES:\n")
            self.path_text.insert(tk.END, "="*50 + "\n")
            for feature, value in features.items():
                self.path_text.insert(tk.END, f"{feature.replace('_', ' ').title()}: {value}\n")

            self.path_text.insert(tk.END, "\nDECISION PATH:\n")
            self.path_text.insert(tk.END, "="*50 + "\n")
            for i, step in enumerate(path, 1):
                self.path_text.insert(tk.END, f"{i}. {step}\n")

            self.path_text.insert(tk.END, f"\nHASIL AKHIR: {result}\n")
            self.path_text.insert(tk.END, "="*50 + "\n")

            recommendations = {
                "Insomnia": "Rekomendasi: Konsultasi dengan dokter, atur jadwal tidur teratur, hindari kafein sebelum tidur.",
                "Sleep Apnea": "Rekomendasi: Konsultasi dengan dokter spesialis tidur, pertimbangkan sleep study, jaga berat badan ideal.",
                "None": "Kondisi tidur normal. Pertahankan pola hidup sehat dan olahraga teratur."
            }
            self.path_text.insert(tk.END, f"\n{recommendations.get(result, '')}\n")

        except ValueError as e:
            messagebox.showerror("Error", f"Input tidak valid: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

    def show_decision_tree(self):
        try:
            dot, _ = visualize_tree_graphviz(self.tree_predictor.root)
            image_data = dot.pipe(format='png')
            image = Image.open(io.BytesIO(image_data))
            image = image.resize((600, 400), Image.Resampling.LANCZOS)
            image_tk = ImageTk.PhotoImage(image)

            top = tk.Toplevel(self.root)
            top.title("Visualisasi Pohon Keputusan")
            top.geometry("640x450")
            label = tk.Label(top, image=image_tk)
            label.image = image_tk
            label.pack(padx=10, pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Gagal menampilkan pohon keputusan: {str(e)}")

def main():
    root = tk.Tk()
    app = SleepDisorderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

