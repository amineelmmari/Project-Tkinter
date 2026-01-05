import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

class Equipment:
    def __init__(self, id, name, category, manufacturer, serial_number, 
                 purchase_date, status, location):
        self.id = id
        self.name = name
        self.category = category
        self.manufacturer = manufacturer
        self.serial_number = serial_number
        self.purchase_date = purchase_date
        self.status = status
        self.location = location
        self.maintenance_history = []
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'manufacturer': self.manufacturer,
            'serial_number': self.serial_number,
            'purchase_date': self.purchase_date,
            'status': self.status,
            'location': self.location,
            'maintenance_history': self.maintenance_history
        }
    
    @staticmethod
    def from_dict(data):
        eq = Equipment(
            data['id'], data['name'], data['category'],
            data['manufacturer'], data['serial_number'],
            data['purchase_date'], data['status'], data['location']
        )
        eq.maintenance_history = data.get('maintenance_history', [])
        return eq


class BiomedicalEquipmentManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion d'Équipements Biomédicaux")
        self.root.geometry("1000x600")
        
        self.equipments = []
        self.next_id = 1
        self.data_file = "equipments_data.json"
        
        self.load_data()
        
        self.create_widgets()
        
    def create_widgets(self):
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X)
        title_label = tk.Label(title_frame, text="Système de Gestion d'Équipements Biomédicaux",
                               font=("Arial", 18, "bold"), bg="#2c3e50", fg="white")
        title_label.pack(pady=15)
        
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_frame = tk.LabelFrame(main_frame, text="Informations de l'Équipement", 
                                   font=("Arial", 12, "bold"), padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        
        fields = [
            ("Nom:", "name"),
            ("Catégorie:", "category"),
            ("Fabricant:", "manufacturer"),
            ("N° Série:", "serial_number"),
            ("Date d'Achat:", "purchase_date"),
            ("Localisation:", "location")
        ]
        
        self.entries = {}
        for i, (label_text, field_name) in enumerate(fields):
            label = tk.Label(left_frame, text=label_text, font=("Arial", 10))
            label.grid(row=i, column=0, sticky=tk.W, pady=5)
            
            entry = tk.Entry(left_frame, width=25, font=("Arial", 10))
            entry.grid(row=i, column=1, pady=5, padx=5)
            self.entries[field_name] = entry
        
        tk.Label(left_frame, text="Statut:", font=("Arial", 10)).grid(
            row=len(fields), column=0, sticky=tk.W, pady=5)
        self.status_var = tk.StringVar()
        status_combo = ttk.Combobox(left_frame, textvariable=self.status_var,
                                    values=["Opérationnel", "En maintenance", 
                                           "Hors service", "En calibration"],
                                    width=23, state="readonly")
        status_combo.grid(row=len(fields), column=1, pady=5, padx=5)
        status_combo.current(0)
        
        button_frame = tk.Frame(left_frame)
        button_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=15)
        
        tk.Button(button_frame, text="Ajouter", command=self.add_equipment,
                 bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                 width=10).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Modifier", command=self.update_equipment,
                 bg="#f39c12", fg="white", font=("Arial", 10, "bold"),
                 width=10).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Supprimer", command=self.delete_equipment,
                 bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
                 width=10).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Effacer", command=self.clear_fields,
                 bg="#95a5a6", fg="white", font=("Arial", 10, "bold"),
                 width=10).pack(side=tk.LEFT, padx=5)
        
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        search_frame = tk.Frame(right_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(search_frame, text="Rechercher:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search_equipment())
        tk.Entry(search_frame, textvariable=self.search_var, 
                width=30, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        tree_frame = tk.Frame(right_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar.set,
                                 selectmode="browse")
        self.tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
        
        self.tree['columns'] = ('ID', 'Nom', 'Catégorie', 'Fabricant', 
                                'N° Série', 'Statut', 'Localisation')
        
        self.tree.column('#0', width=0, stretch=tk.NO)
        self.tree.column('ID', width=40, anchor=tk.CENTER)
        self.tree.column('Nom', width=120, anchor=tk.W)
        self.tree.column('Catégorie', width=100, anchor=tk.W)
        self.tree.column('Fabricant', width=100, anchor=tk.W)
        self.tree.column('N° Série', width=80, anchor=tk.W)
        self.tree.column('Statut', width=100, anchor=tk.CENTER)
        self.tree.column('Localisation', width=100, anchor=tk.W)
        
        for col in self.tree['columns']:
            self.tree.heading(col, text=col, anchor=tk.CENTER)
        
        self.tree.bind('<ButtonRelease-1>', self.on_tree_select)
        
        self.status_bar = tk.Label(self.root, text="Prêt", 
                                   bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.display_equipments()
    
    def add_equipment(self):
        if not self.validate_inputs():
            return
        
        equipment = Equipment(
            self.next_id,
            self.entries['name'].get(),
            self.entries['category'].get(),
            self.entries['manufacturer'].get(),
            self.entries['serial_number'].get(),
            self.entries['purchase_date'].get(),
            self.status_var.get(),
            self.entries['location'].get()
        )
        
        self.equipments.append(equipment)
        self.next_id += 1
        
        self.display_equipments()
        self.clear_fields()
        self.save_data()
        
        self.status_bar.config(text=f"Équipement '{equipment.name}' ajouté avec succès")
        messagebox.showinfo("Succès", "Équipement ajouté avec succès!")
    
    def update_equipment(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner un équipement à modifier")
            return
        
        if not self.validate_inputs():
            return
        
        item = self.tree.item(selected[0])
        eq_id = int(item['values'][0])
        
        for eq in self.equipments:
            if eq.id == eq_id:
                eq.name = self.entries['name'].get()
                eq.category = self.entries['category'].get()
                eq.manufacturer = self.entries['manufacturer'].get()
                eq.serial_number = self.entries['serial_number'].get()
                eq.purchase_date = self.entries['purchase_date'].get()
                eq.status = self.status_var.get()
                eq.location = self.entries['location'].get()
                break
        
        self.display_equipments()
        self.clear_fields()
        self.save_data()
        
        self.status_bar.config(text=f"Équipement ID {eq_id} modifié avec succès")
        messagebox.showinfo("Succès", "Équipement modifié avec succès!")
    
    def delete_equipment(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner un équipement à supprimer")
            return
        
        item = self.tree.item(selected[0])
        eq_id = int(item['values'][0])
        eq_name = item['values'][1]
        
        if messagebox.askyesno("Confirmation", 
                               f"Êtes-vous sûr de vouloir supprimer '{eq_name}'?"):
            self.equipments = [eq for eq in self.equipments if eq.id != eq_id]
            self.display_equipments()
            self.clear_fields()
            self.save_data()
            
            self.status_bar.config(text=f"Équipement '{eq_name}' supprimé")
            messagebox.showinfo("Succès", "Équipement supprimé avec succès!")
    
    def display_equipments(self, equipments_list=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        display_list = equipments_list if equipments_list is not None else self.equipments
        
        for eq in display_list:
            self.tree.insert('', tk.END, values=(
                eq.id, eq.name, eq.category, eq.manufacturer,
                eq.serial_number, eq.status, eq.location
            ))
        
        count = len(display_list)
        self.status_bar.config(text=f"Total: {count} équipement(s)")
    
    def search_equipment(self):
        search_term = self.search_var.get().lower()
        
        if not search_term:
            self.display_equipments()
            return
        
        filtered = [eq for eq in self.equipments if
                   search_term in eq.name.lower() or
                   search_term in eq.category.lower() or
                   search_term in eq.manufacturer.lower()]
        
        self.display_equipments(filtered)
    
    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        values = item['values']
        
        eq_id = int(values[0])
        for eq in self.equipments:
            if eq.id == eq_id:
                self.entries['name'].delete(0, tk.END)
                self.entries['name'].insert(0, eq.name)
                
                self.entries['category'].delete(0, tk.END)
                self.entries['category'].insert(0, eq.category)
                
                self.entries['manufacturer'].delete(0, tk.END)
                self.entries['manufacturer'].insert(0, eq.manufacturer)
                
                self.entries['serial_number'].delete(0, tk.END)
                self.entries['serial_number'].insert(0, eq.serial_number)
                
                self.entries['purchase_date'].delete(0, tk.END)
                self.entries['purchase_date'].insert(0, eq.purchase_date)
                
                self.entries['location'].delete(0, tk.END)
                self.entries['location'].insert(0, eq.location)
                
                self.status_var.set(eq.status)
                break
    
    def clear_fields(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.status_var.set("Opérationnel")
        self.tree.selection_remove(self.tree.selection())
    
    def validate_inputs(self):
        if not self.entries['name'].get():
            messagebox.showerror("Erreur", "Le nom est obligatoire")
            return False
        if not self.entries['category'].get():
            messagebox.showerror("Erreur", "La catégorie est obligatoire")
            return False
        if not self.entries['manufacturer'].get():
            messagebox.showerror("Erreur", "Le fabricant est obligatoire")
            return False
        return True
    
    def save_data(self):
        data = [eq.to_dict() for eq in self.equipments]
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump({'equipments': data, 'next_id': self.next_id}, 
                         f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder: {str(e)}")
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.equipments = [Equipment.from_dict(eq) for eq in data['equipments']]
                    self.next_id = data.get('next_id', 1)
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger les données: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = BiomedicalEquipmentManager(root)
    root.mainloop()
