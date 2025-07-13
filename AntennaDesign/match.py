# pip install scikit-rf matplotlib numpy
import numpy as np
import matplotlib.pyplot as plt
import skrf as rf
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 周波数設定
f = np.linspace(10e6, 30e6, 1000)
w = 2 * np.pi * f

Z0 = 50
#R1 = 1.8
#Rload = 2.29
#Lload = 2.37e-6
#Cload = 3.40e-12
R1 = 0.1
Rload = 4.03
Lload = 1.581e-6
Cload = 9.43e-12

fc0 = 14.3e6
f_marker = 13.56e6
idx_marker = np.argmin(np.abs(f - f_marker))

def simulate_zin(L0, C0, C1, C2):
    Zin_list = []
    for wi in w:
        Y = np.zeros((10, 10), dtype=complex)
        def add_admittance(n1, n2, Yval):
            if n1 != 0:
                Y[n1, n1] += Yval
            if n2 != 0:
                Y[n2, n2] += Yval
            if n1 != 0 and n2 != 0:
                Y[n1, n2] -= Yval
                Y[n2, n1] -= Yval
        Yval_L1 = 1 / (1j * wi * L0)
        add_admittance(9, 1, Yval_L1)
        add_admittance(0, 2, 1 / (1j * wi * L0))
        add_admittance(1, 3, 1j * wi * C0)
        add_admittance(2, 3, 1j * wi * C0)
        add_admittance(1, 4, 1j * wi * C1)
        add_admittance(4, 3, 1j * wi * C2)
        add_admittance(2, 5, 1j * wi * C1)
        add_admittance(5, 3, 1j * wi * C2)
        add_admittance(4, 6, 1 / R1)
        add_admittance(5, 7, 1 / R1)
        add_admittance(6, 8, 1 / Rload)
        add_admittance(8, 7, 1 / (1j * wi * Lload))
        add_admittance(6, 7, 1j * wi * Cload)
        known_voltages = {0: 0, 9: 1}
        unknowns = [i for i in range(10) if i not in known_voltages]
        Y_reduced = Y[np.ix_(unknowns, unknowns)]
        I_reduced = -Y[np.ix_(unknowns, list(known_voltages.keys()))] @ np.array([known_voltages[k] for k in known_voltages])
        try:
            V_partial = np.linalg.solve(Y_reduced, I_reduced)
            V = np.zeros(10, dtype=complex)
            for idx, node in enumerate(unknowns):
                V[node] = V_partial[idx]
            for node, val in known_voltages.items():
                V[node] = val
            Iin = (V[9] - V[1]) * Yval_L1
            Zin = 1 / Iin
        except np.linalg.LinAlgError:
            Zin = np.nan
        Zin_list.append(Zin)
    return np.array(Zin_list)

# Tkinter GUI
root = tk.Tk()
root.title("Impedance Viewer")

main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

fig = plt.Figure(figsize=(8, 4))
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=main_frame)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

L0_var = tk.DoubleVar(value=270.0)
C0_var = tk.DoubleVar(value=0.0)  # 初期値は後で更新
C1_var = tk.DoubleVar(value=18.0)
C2_var = tk.DoubleVar(value=68.0)
view_mode = tk.StringVar(value="smith")

slider_frame = ttk.Frame(main_frame)
slider_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
slider_frame.columnconfigure(1, weight=1)

def update_chart(event=None):
    try:
        L0 = float(L0_entry.get())
        C1 = float(C1_entry.get())
        C2 = float(C2_entry.get())
        C0 = float(C0_entry.get())
    except ValueError:
        return

    L0_val_label.config(text=f"{L0:.1f} nH")
    C1_val_label.config(text=f"{C1:.1f} pF")
    C2_val_label.config(text=f"{C2:.1f} pF")

    Zin_list = simulate_zin(L0 * 1e-9, C0 * 1e-12, C1 * 1e-12, C2 * 1e-12)
    Zin_valid = Zin_list[~np.isnan(Zin_list)]
    f_valid = f[~np.isnan(Zin_list)]

    ax.clear()
    if len(Zin_valid) > 0:
        if view_mode.get() == "smith":
            nw = rf.Network(frequency=f_valid, z=Zin_valid, f_unit='Hz', z0=Z0)
            nw.plot_s_smith(ax=ax)
            gamma_marker = (Zin_list[idx_marker] - Z0) / (Zin_list[idx_marker] + Z0)
            ax.plot(np.real(gamma_marker), np.imag(gamma_marker), 'ro', label='13.56 MHz')
            ax.set_title("Smith Chart")
            ax.set_aspect("equal", adjustable="box")
        else:
            ax.plot(f_valid / 1e6, np.real(Zin_valid), label="Re(Z)")
            ax.plot(f_valid / 1e6, np.imag(Zin_valid), label="Im(Z)")
            ax.axvline(x=13.56, color='red', linestyle='--', label='13.56 MHz')
            imag = np.imag(Zin_valid)
            crossings = np.where(np.diff(np.sign(imag)) != 0)[0]
            for idx in crossings:
                f1, f2 = f_valid[idx], f_valid[idx + 1]
                im1, im2 = imag[idx], imag[idx + 1]
                f_zero = f1 - im1 * (f2 - f1) / (im2 - im1)
                ax.axvline(x=f_zero / 1e6, color='blue', linestyle='--', label='Im(Z) = 0' if idx == crossings[0] else None)
            ax.set_xlim(12, 15)
            ax.set_xlabel("Frequency [MHz]")
            ax.set_ylabel("Impedance [Ohm]")
            ax.set_title("Zin Real/Imag")
            ax.set_aspect("auto")
            ax.legend()
        Zin_marker = Zin_list[idx_marker]
        if not np.isnan(Zin_marker):
            Zmarker_label.config(text=f"Z @ 13.56 MHz: {np.real(Zin_marker):.1f} + j{np.imag(Zin_marker):.1f} Ω")
        else:
            Zmarker_label.config(text="Z @ 13.56 MHz: -")
    else:
        Zmarker_label.config(text="Z @ 13.56 MHz: -")
    canvas.draw()

def update_C0_from_L0(*args):
    try:
        L0 = L0_var.get()
        C0 = 1 / ((2 * np.pi * fc0) ** 2 * (L0 * 1e-9))
        C0_var.set(C0 * 1e12)
        C0_entry.delete(0, tk.END)
        C0_entry.insert(0, f"{C0 * 1e12:.2f}")
        update_chart()
    except Exception:
        pass

L0_var.trace_add("write", update_C0_from_L0)

def add_slider_with_entry(label, var, from_, to, row):
    ttk.Label(slider_frame, text=label).grid(row=row, column=0, sticky=tk.W)
    scale = ttk.Scale(slider_frame, variable=var, from_=from_, to=to, orient="horizontal", command=update_chart)
    scale.grid(row=row, column=1, sticky=tk.EW)
    entry = ttk.Entry(slider_frame, textvariable=var, width=8)
    entry.grid(row=row, column=2, sticky=tk.W)
    return ttk.Label(slider_frame, textvariable=var), entry

L0_val_label, L0_entry = add_slider_with_entry("L0 [nH]", L0_var, 150, 800, 0)
C1_val_label, C1_entry = add_slider_with_entry("C1 [pF]", C1_var, 5, 60, 1)
C2_val_label, C2_entry = add_slider_with_entry("C2 [pF]", C2_var, 20, 200, 2)

# C0 テキスト入力欄
ttk.Label(slider_frame, text="C0 [pF]").grid(row=3, column=0, sticky=tk.W)
C0_entry = ttk.Entry(slider_frame, textvariable=C0_var, width=8)
C0_entry.grid(row=3, column=1, sticky=tk.W)
C0_entry.bind("<Return>", update_chart)

Zmarker_label = ttk.Label(slider_frame, text="Z @ 13.56 MHz: -")
Zmarker_label.grid(row=4, column=0, columnspan=3, sticky=tk.W)

radio_frame = ttk.Frame(slider_frame)
radio_frame.grid(row=5, column=0, columnspan=3, sticky=tk.W)
ttk.Label(radio_frame, text="View:").pack(side=tk.LEFT)
ttk.Radiobutton(radio_frame, text="Smith", variable=view_mode, value="smith", command=update_chart).pack(side=tk.LEFT)
ttk.Radiobutton(radio_frame, text="Re/Im", variable=view_mode, value="zplot", command=update_chart).pack(side=tk.LEFT)

# 初期 C0 計算
initial_C0 = 1 / ((2 * np.pi * fc0) ** 2 * (L0_var.get() * 1e-9))
C0_var.set(initial_C0 * 1e12)
C0_entry.delete(0, tk.END)
C0_entry.insert(0, f"{initial_C0 * 1e12:.2f}")

update_chart()
root.mainloop()
