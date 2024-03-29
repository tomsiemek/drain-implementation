"""
Basic version with only first token split and static similarity threshold
"""

import re
from preprocessor import Preprocessor
from math import log


DIGITS_RE = re.compile('\d')
def contains_digits(string):
    return DIGITS_RE.search(string)



class Cluster:
    cluster_counter = 0
    PLACEHOLDER = "<*>"

    def __init__(self, tokens: [str]):
        self.template_tokens = tokens
        self.number_of_consts = len(tokens)
        self.id = f"#{Cluster.cluster_counter}"
        self.found_messages = 1
        Cluster.cluster_counter += 1
        number_of_variable_candidates = 0
        for token in tokens:
            if contains_digits(token):
                number_of_variable_candidates += 1
        self.st_base = max(2, number_of_variable_candidates + 1)
        self.st_init = 0.5 * (len(tokens) - number_of_variable_candidates) / len(tokens)
        self.similarity_threshold = self.st_init


    def compare(self, tokens: [str]):
        """
        Returns similarity value between given tokens and cluster.
        """
        identity_count = 0
        for template, token in zip(self.template_tokens, tokens):
            if template != Cluster.PLACEHOLDER and template == token:
                identity_count += 1
        similarity = identity_count / self.number_of_consts
        return similarity if similarity >= self.similarity_threshold else 0
        
    def update_template(self, tokens: [str]):
        self.found_messages += 1
        for i in range(len(tokens)):
            if self.template_tokens[i] != Cluster.PLACEHOLDER and self.template_tokens[i] != tokens[i]:
                self.template_tokens[i] = Cluster.PLACEHOLDER
                self.number_of_consts -= 1
        self.similarity_threshold = min(1, self.st_init + 0.5 * log(len(tokens) - self.number_of_consts + 1, self.st_base))
    def __str__(self):
        return f"{self.id} found_messages: {self.found_messages} st: {self.similarity_threshold} template: {' '.join(self.template_tokens)}"


class Drain:
    FIRST_TOKEN = 0
    LAST_TOKEN = 1 
    NO_SPLIT_TOKEN = 2
    def __init__(self):
        self.length_nodes = {}
        self.clusters = []
        self.preprocessor = Preprocessor()
        self.re_placeholder = re.compile(r'<\w+>')

    def parse_message(self, message_raw: str):
        """
        Returns found cluster.

        Raise Exception: "Empty string".
        """
        tokens = self.preprocessor.preprocess(message_raw)
        if len(tokens) == 0:
            raise "Empty string."
        cluster = self.search(tokens)
        return f"{cluster.id} -> {' '.join(cluster.template_tokens)}"

    def look_for_suitable_cluster(self, tokens: [str], clusters: [Cluster]):
        """
        Looks for most fitting cluster which matches given tokens among given clusters.
        """
        max_val = 0
        max_cluster = None
        similarity = 0
        for cluster in clusters:
            similarity = cluster.compare(tokens)
            if max_val < similarity:
                max_val = similarity
                max_cluster = cluster
        return max_cluster
    

    def is_placeholder(self, token):
        return True if self.re_placeholder.match(token) else False

    def determine_split_token_flag(self, tokens: [str]):
        """
        Determines which split token should be used to route the tree.
        """
        first_token = tokens[0]
        last_token = tokens[len(tokens) - 1]
        if contains_digits(first_token) or self.is_placeholder(first_token):
            if contains_digits(last_token) or self.is_placeholder(last_token):
                if self.is_placeholder(last_token):
                    return Drain.LAST_TOKEN
                elif self.is_placeholder(first_token):
                    return Drain.FIRST_TOKEN
                return Drain.NO_SPLIT_TOKEN
            else:
                return Drain.LAST_TOKEN
        return Drain.FIRST_TOKEN
    
    def search(self, tokens: [str]):
        """
        Looks for cluster which matches given tokens.
        """
        length = len(tokens)
        split_token_flag = self.determine_split_token_flag(tokens)

        if split_token_flag == Drain.FIRST_TOKEN:
            split_token = tokens[0]
        elif split_token_flag == Drain.LAST_TOKEN:
            split_token = tokens[length - 1]
        # node representing given length exist
        if length in self.length_nodes:
            split_token_nodes = self.length_nodes[length][split_token_flag]
            if split_token_flag == Drain.NO_SPLIT_TOKEN:
                clusters = self.length_nodes[length][split_token_flag]
            else:
                split_token_nodes = self.length_nodes[length][split_token_flag]
                if split_token in split_token_nodes:
                    clusters = split_token_nodes[split_token]
                # if there is no given split token           
                else:
                    new_cluster = Cluster(tokens)
                    clusters = [new_cluster]
                    split_token_nodes[split_token] = clusters
                    self.clusters.append(new_cluster)
                    return new_cluster
            best_cluster = self.look_for_suitable_cluster(tokens, clusters)
            # if found cluster have necessary similarity
            if best_cluster:
                best_cluster.update_template(tokens)
                return best_cluster
            # there is no matching cluster, creating new one
            else:
                new_cluster = Cluster(tokens)
                clusters.append(new_cluster)
                self.clusters.append(new_cluster)
                return new_cluster
        # there is no node representing given length
        else:
            new_cluster = Cluster(tokens)
            clusters = [new_cluster]
            self.length_nodes[length] = {Drain.FIRST_TOKEN: {}, Drain.LAST_TOKEN: {}, Drain.NO_SPLIT_TOKEN: []}
            if split_token_flag == Drain.NO_SPLIT_TOKEN:
                self.length_nodes[length][split_token_flag] = clusters
            else:
                self.length_nodes[length][split_token_flag][split_token] = clusters
            self.clusters.append(new_cluster)
            return new_cluster

    def give_cluster_list(self):
        return [str(cluster) for cluster in self.clusters]
    def give_tree(self):
        """
        Returns string with representation of parse tree.
        """
        output_string = f"Number_of_clusters: {len(self.clusters)}, different length nodes: {len(self.length_nodes)}\n"
        tab = "    "
        for length, nodes in self.length_nodes.items():
            output_string += f"Length: {length}\n"
            if nodes[Drain.FIRST_TOKEN]:
                output_string += tab + "First_token\n"
                for token, clusters in nodes[Drain.FIRST_TOKEN].items():
                    output_string += tab * 2 + token + "\n"
                    for cluster in clusters:
                        output_string += tab * 3 + str(cluster) + "\n"
            if nodes[Drain.LAST_TOKEN]:
                output_string += tab + "Last_token\n"
                for token, clusters in nodes[Drain.LAST_TOKEN].items():
                    output_string += tab * 2 + token + "\n"
                    for cluster in clusters:
                        output_string += tab * 3 + str(cluster) + "\n"
            if nodes[Drain.NO_SPLIT_TOKEN]:
                output_string += tab + "No_split_token\n"
                clusters = nodes[Drain.NO_SPLIT_TOKEN]
                for cluster in clusters:
                    output_string += tab * 3 + str(cluster) + "\n"
        return output_string


if __name__ == "__main__":
    example_logs = [
        "I ate 8 soups today",
        "I ate 20 soups today",
        "I ate 69 soups yesterday",
        "send info to the server",
        "send yo_mama to the server",
        "2016-09-28 04:30:31, Info CBS Warning: Unrecognized packageExtended attribute.",
        "I hate barbacue sauce fiercly.",
        "I love going for walks.",
        "205.189.154.54 - - [01/Jul/1995:00:01:19 -0400] \"GET /shuttle/missions/sts-71/images/KSC-95EC-0423.txt HTTP/1.0\" 200 1224",
        "015-10-18 <TIME> WARN [RMCommunicator Allocator] org.apache.hadoop.ipc.Client: Address change detected. Old: msra-sa-41<IP> New: msra-sa-41:8030"
    ]
    drain = Drain()
    for l in example_logs:
        print(l)
        print(drain.parse_message(l))
    print(drain.give_cluster_list())
    print("'\n\n'")
    print(drain.give_tree())
