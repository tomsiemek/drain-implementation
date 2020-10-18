"""
Basic version with only length layer and static similarity threshold
"""

class Cluster:
    cluster_counter = 0
    PLACEHOLDER = "<*>"

    def __init__(self, tokens: [str]):
        self.template_tokens = tokens
        self.number_of_consts = len(tokens)
        self.id = f"#{Cluster.cluster_counter}"
        Cluster.cluster_counter += 1

    def compare(self, tokens: [str]):
        """
        Returns similarity value between given tokens and cluster.
        """
        identity_count = 0
        for template, token in zip(self.template_tokens, tokens):
            if template != Cluster.PLACEHOLDER and template == token:
                identity_count += 1
        return identity_count / self.number_of_consts
        
    def update_template(self, tokens: [str]):
        for i in range(len(tokens)):
            if self.template_tokens[i] != Cluster.PLACEHOLDER and self.template_tokens[i] != tokens[i]:
                self.template_tokens[i] = Cluster.PLACEHOLDER
                self.number_of_consts -= 1


class Drain:
    def __init__(self):
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
        Looks for most fitting cluster which matches given tokens among given clusters.
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
            # for now split based on first token
            split_token_nodes = self.length_nodes[length]
            split_token = tokens[0]

            if split_token in split_token_nodes:
                clusters = split_token_nodes[split_token]           
            else:
                new_cluster = Cluster(tokens)
                clusters = [new_cluster]
                split_token_nodes[split_token] = clusters
                self.clusters.append(new_cluster)
                return new_cluster
            similarity, best_cluster = self.look_for_suitable_cluster(tokens, clusters)
            if similarity > self.similarity_threshold:
                best_cluster.update_template(tokens)
                return best_cluster
            else:
                new_cluster = Cluster(tokens)
                split_token_nodes[split_token].append(new_cluster)
                self.clusters.append(new_cluster)
                return new_cluster
        # there is no node representing given length
        else:
            new_cluster = Cluster(tokens)
            clusters = [new_cluster]
            self.length_nodes[length] = {str(tokens[0]): clusters}
            self.clusters.append(new_cluster)
            return new_cluster


if __name__ == "__main__":
    example_logs = [
        "I ate 8 soups today",
        "I ate 20 soups today",
        "I ate 69 soups yesterday",
        "send info to the server",
        "send yo_mama to the server",
        "2016-09-28 04:30:31, Info CBS Warning: Unrecognized packageExtended attribute.",
        "I hate barbacue sauce fiercly.",
        "I love going for walks."
    ]
    drain = Drain()
    for l in example_logs:
        print(l)
        print(drain.parse_message(l))