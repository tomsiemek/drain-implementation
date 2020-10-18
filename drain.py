"""
Basic version with only length layer and static similarity threshold
"""

import re


class Cluster:
    cluster_counter = 0
    PLACEHOLDER = "<*>"

    def __init__(self, tokens: [str]):
        self.template_tokens = tokens
        self.number_of_consts = len(tokens)
        self.id = f"#{Cluster.cluster_counter}"
        for t in tokens:
           if re.match(r"[<>]", t):
               self.number_of_consts -= 1
        Cluster.cluster_counter += 1

    def compare(self, tokens: [str]):
        identity_count = 0
        for template, token in zip(self.template_tokens, tokens):
            if not re.match(r"[<>]", template) and template == token:
                identity_count += 1
        return identity_count / self.number_of_consts
        
    def update_template(self, tokens: [str]):
        for i in range(len(tokens)):
            if not re.match(r"[<>]", self.template_tokens[i]) and self.template_tokens[i] != tokens[i]:
                self.template_tokens[i] = Cluster.PLACEHOLDER


class Drain:
    def __init__(self):
        self.token_layers = 1
        self.length_nodes = {}
        self.clusters = []
        self.similarity_threshold = 0.5

    def parse_message(self, message_raw: str):
        """
        Returns found cluster.
        """
        message_stripped = message_raw.strip()
        tokens = message_stripped.split()
        cluster = self.search(tokens)
        return f"{cluster.id} -> {' '.join(cluster.template_tokens)}"

    def look_for_suitable_cluster(self, tokens: [str], clusters: [Cluster]):
        """
        Looks for most fitting cluster which matches given tokens.
        """
        max_val = 0
        max_cluster = None
        for cluster in clusters:
            similarity = cluster.compare(tokens)
            if max_val < similarity:
                max_val = similarity
                max_cluster = cluster
        return (similarity, max_cluster)
    def search(self, tokens: [str]):
        """
        Looks for cluster which matches given tokens.
        """
        length = len(tokens)
        if length in self.length_nodes:
            clusters = self.length_nodes[length]
            similarity, best_cluster = self.look_for_suitable_cluster(tokens, clusters)
            if similarity > self.similarity_threshold:
                best_cluster.update_template(tokens)
                return best_cluster
            else:
                new_cluster = Cluster(tokens)
                self.length_nodes[length].append(new_cluster)
                self.clusters.append(new_cluster)
                return new_cluster
        else:
            new_cluster = Cluster(tokens)
            self.length_nodes[length] = [new_cluster]
            self.clusters.append(new_cluster)
            return new_cluster


if __name__ == "__main__":
    example_logs = [
        "I ate 8 soups today",
        "I ate 20 soups today",
        "I ate 69 soups yesterday",
        "send info to the server",
        "send yo_mama to the server",
        "2016-09-28 04:30:31, Info CBS Warning: Unrecognized packageExtended attribute."
    ]
    drain = Drain()
    for l in example_logs:
        print(l)
        print(drain.parse_message(l))