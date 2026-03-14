import re
import sqlite3
import os

class GraphEngine:
    def __init__(self, db_path="kore.db"):
        # We assume db is in the root or database folder, depending on cwd
        # Try to find it if not provided an absolute path
        if not os.path.exists(db_path):
            alt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "kore.db")
            if os.path.exists(alt_path):
                db_path = alt_path
            else:
                alt_path2 = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "kore.db")
                if os.path.exists(alt_path2):
                    db_path = alt_path2
                    
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path, timeout=5)

    def extract_tags(self, text):
        """Extracts #tags from a given text, ignoring case."""
        if not text:
            return []
        # Find all words starting with '#' containing letters, numbers or hyphens
        tags = set(re.findall(r'#[\w-]+', text, re.IGNORECASE))
        return [t.lower() for t in tags]

    def build_graph_data(self):
        """
        Scans the database and builds the nodes and edges for the Knowledge Graph.
        Nodes are dictionaries.
        Edges are dictionaries with 'source' and 'target' node IDs.
        """
        nodes = []
        edges = []
        
        # We will keep track of which entities have which tags
        # { "#tag": ["node_id_1", "node_id_2"] }
        tag_map = {}
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 1. Journal Entries
                cursor.execute("SELECT id, title, content, keywords FROM journal")
                for row in cursor.fetchall():
                    j_id, title, content, keywords = row
                    node_id = f"journal_{j_id}"
                    
                    combined_text = f"{title} {content} {keywords if keywords else ''}"
                    tags = self.extract_tags(combined_text)
                    
                    if tags: # Only include logs that have tags
                        nodes.append({
                            "id": node_id,
                            "type": "journal",
                            "label": title,
                            "desc": content[:100] + "..." if len(content) > 100 else content,
                            "tags": tags,
                            "color": "#ff3b30", # Red for journal
                            "mass": 1.5 + (len(tags) * 0.2)
                        })
                        for t in tags:
                            if t not in tag_map: tag_map[t] = []
                            tag_map[t].append(node_id)

                # 2. Projects
                cursor.execute("SELECT id, name, description FROM projects")
                for row in cursor.fetchall():
                    p_id, name, desc = row
                    node_id = f"project_{p_id}"
                    
                    combined_text = f"{name} {desc if desc else ''}"
                    tags = self.extract_tags(combined_text)
                    
                    if tags:
                        nodes.append({
                            "id": node_id,
                            "type": "project",
                            "label": name,
                            "desc": desc if desc else "",
                            "tags": tags,
                            "color": "#ff9500", # Orange for projects
                            "mass": 2.0 + (len(tags) * 0.3)
                        })
                        for t in tags:
                            if t not in tag_map: tag_map[t] = []
                            tag_map[t].append(node_id)
                
                # 3. SRS Topics
                cursor.execute("SELECT id, name, category FROM topics")
                for row in cursor.fetchall():
                    t_id, name, cat = row
                    node_id = f"topic_{t_id}"
                    
                    # For topics, the name and category themselves might be tags. 
                    # We also manually create a tag based on the category.
                    combined_text = f"{name} #{cat.replace(' ', '')}"
                    tags = self.extract_tags(combined_text)
                    
                    nodes.append({
                        "id": node_id,
                        "type": "topic",
                        "label": name,
                        "desc": f"Category: {cat}",
                        "tags": tags,
                        "color": "#5856d6", # Purple for Intelligence/SRS
                        "mass": 1.2
                    })
                    for t in tags:
                        if t not in tag_map: tag_map[t] = []
                        tag_map[t].append(node_id)
                        
                # 4. Homework
                cursor.execute("SELECT id, subject, title FROM homework")
                for row in cursor.fetchall():
                    h_id, subj, title = row
                    node_id = f"homework_{h_id}"
                    
                    combined_text = f"{title} #{subj.replace(' ', '')}"
                    tags = self.extract_tags(combined_text)
                    
                    if tags:
                        nodes.append({
                            "id": node_id,
                            "type": "homework",
                            "label": title,
                            "desc": f"Subject: {subj}",
                            "tags": tags,
                            "color": "#4cd964", # Green for homework
                            "mass": 1.0
                        })
                        for t in tags:
                            if t not in tag_map: tag_map[t] = []
                            tag_map[t].append(node_id)

        except sqlite3.Error as e:
            print(f"Database error in GraphEngine: {e}")
            return {"nodes": [], "edges": [], "tags": {}}

        # Create tag nodes (Hubs) to visually anchor the web
        for tag, connected_nodes in tag_map.items():
            if len(connected_nodes) > 1: # Only create a hub if it connects multiple things
                tag_node_id = f"tag_{tag}"
                nodes.append({
                    "id": tag_node_id,
                    "type": "tag",
                    "label": tag,
                    "desc": f"Hub de tag connectant {len(connected_nodes)} éléments.",
                    "tags": [tag],
                    "color": "#0a84ff", # Standard blue for tags
                    "mass": 3.0 + (len(connected_nodes) * 0.5) # Bigger mass = stronger anchor
                })
                
                # Create edges linking the source nodes to this Tag Hub
                for n_id in connected_nodes:
                    edges.append({
                        "source": n_id,
                        "target": tag_node_id,
                        "strength": 1.0
                    })
            elif len(connected_nodes) == 1:
                # If a tag is only used once, we don't necessarily need a hub,
                # but we keep it in the node's list of tags for searchability.
                pass

        return {
            "nodes": nodes,
            "edges": edges,
            "tags": list(tag_map.keys())
        }

if __name__ == "__main__":
    # Test
    ge = GraphEngine()
    data = ge.build_graph_data()
    print(f"Graph Data Built: {len(data['nodes'])} Nodes, {len(data['edges'])} Edges.")
    for n in data['nodes'][:5]:
        print(n)
