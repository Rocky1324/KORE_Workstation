from datetime import datetime, timedelta

class SRSAlgorithm:
    """
    Implémentation basique de l'algorithme SuperMemo-2 (SM-2) pour la répétition espacée.
    """
    @staticmethod
    def calculate_next_review(quality: int, current_interval: int, current_ease: float) -> tuple[str, int, float]:
        """
        Calcule la prochaine date de révision, le nouvel intervalle et la nouvelle facilité (ease_factor).
        
        :param quality: Un entier de 0 à 5 d'après la difficulté de la réponse:
                        0: Oubli complet
                        1: Fausse réponse avec un souvenir que la bonne réponse existait
                        2: Fausse réponse, mais la bonne réponse semblait familière
                        3: Bonne réponse rappelée avec difficulté
                        4: Bonne réponse rappelée avec hésitation 
                        5: Bonne réponse rappelée parfaitement
        :param current_interval: L'intervalle actuel en jours
        :param current_ease: Le facteur d'aisance actuel (par défaut 2.5)
        :return: (Date au format "YYYY-MM-DD", nouvel intervalle, nouveau facteur d'aisance)
        """
        
        # Mettre à jour l'ease factor
        new_ease = current_ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        
        # L'ease factor ne peut jamais descendre en dessous de 1.3
        if new_ease < 1.3:
            new_ease = 1.3
            
        # Calculer le nouvel intervalle selon la qualité (réponse correcte ou non)
        if quality < 3:
            # Échec ou grande difficulté : retour à la case départ (1 jour)
            new_interval = 1
        else:
            if current_interval == 1:
                new_interval = 6
            elif current_interval == 0:
                new_interval = 1
            else:
                new_interval = round(current_interval * current_ease)

        # Calculer la date précise
        next_date = datetime.now() + timedelta(days=new_interval)
        next_date_str = next_date.strftime("%Y-%m-%d")

        return next_date_str, new_interval, new_ease
