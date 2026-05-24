import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from projekt4 import simulate_numba_with_states

def main():
    parser = argparse.ArgumentParser(
        description='Symulacja modelu Isinga'
    )
    parser.add_argument('--N', type=int, default=100, help='Rozmiar siatki (domyślnie 100)')
    parser.add_argument('--M', type=int, default=500, help='Liczba makrokroków (domyślnie 500)')
    parser.add_argument('-beta', type=float, default=0.4, help='Parametr beta (domyślnie 0.4)')
    parser.add_argument('--B', type=float, default=0.0, help='Pole zewnętrzne (domyślnie 0.0)')
    parser.add_argument('--J', type=float, default=1.0, help='Stała oddziaływania (domyślnie 1.0)')
    parser.add_argument('-magnetization-file', type=str, default=None, help='Plik do zapisu magnetyzacji')
    parser.add_argument('-show-animation', action='store_true', help='Wyświetl animację')
    parser.add_argument('-animation-file', type=str, default=None, help='Plik do zapisu animacji')
    
    args = parser.parse_args()
    
    try:
        if not args.N.is_integer() or not args.M.is_integer():
            raise ValueError("N, M muszą być liczbami całkowitymi")
        if args.N <= 0:
            raise ValueError("N musi być dodatnie")
        if args.M <= 0:
            raise ValueError("M musi być dodatnie")
        if args.beta < 0:
            raise ValueError("beta nie może być ujemna")
        
        # symulacja
        print(f"Uruchamianie symulacji: N={args.N}, M={args.M}, beta={args.beta}, B={args.B}, J={args.J}")
        
        spins = np.random.choice([-1, 1], size=(args.N, args.N))
        E, M, S = simulate_numba_with_states(spins, args.N, args.J, args.beta, args.B, args.M)
        
        print(f"Energia końcowa: {E[-1]:.4f}")
        print(f"Magnetyzacja końcowa: {M[-1]:.4f}")
        
        # zapis magnetyzacji do pliku
        if args.magnetization_file:
            try:
                with open(args.magnetization_file, 'w') as f:
                    for step, mag in enumerate(M):
                        f.write(f"{step},{mag}\n")
                print(f"Magnetyzacja zapisana do {args.magnetization_file}")
            except OSError as e:
                print(f"Błąd przy zapisie magnetyzacji: {e}")
        
        # zapis animacji 
        if args.show_animation or args.animation_file:
            try:
                # Ponownie uruchom symulację ze zbieraniem stanów
                spins = np.random.choice([-1, 1], size=(args.N, args.N))
                E, M, S = simulate_numba_with_states(spins, args.N, args.J, args.beta, args.B, args.M)
                
                fig, ax = plt.subplots(figsize=(6, 6))

                def update(frame):
                    ax.clear()
                    ax.imshow(S[frame], cmap='summer', vmin=-1, vmax=1)
                    ax.set_title(f"Makrokrok {frame}")
                    ax.axis('off')
                    return ax,
        
                anim = FuncAnimation(fig, update, frames=len(S), interval=100, repeat=True)

                if args.animation_file:
                    anim.save(args.animation_file)
                    print(f"Animacja zapisana do {args.animation_file}")
        
                if args.show_animation:
                    plt.show()

                plt.close(fig)
            except Exception as e:
                print(f"Błąd przy tworzeniu animacji: {e}")
        
    except ValueError as e:
        print(f"Błąd wartości parametru: {e}")
    except OSError as e:
        print(f"Błąd systemu plików: {e}")
    except Exception as e:
        print(f"Nieoczekiwany błąd: {e}")

if __name__ == '__main__':
    main()