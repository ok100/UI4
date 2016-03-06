#!/usr/bin/env python

import re
import itertools


class Rule:
    def __init__(self, name, requirements, actions):
        self.name = name
        self.requirements = self._split(requirements)
        self.actions = self._split(actions)

    @staticmethod
    def _split(s):
        return [x.replace('(', '').replace(')', '') for x in s.split(')(')]

    @staticmethod
    def read(file_name):
        with open(file_name) as f:
            lines = [l.strip() for l in f.read().splitlines() if l.strip()]
        rules = []
        while lines:
            name = lines.pop(0).split(':', 1)[0].strip()
            requirement = lines.pop(0).split('AK', 1)[1].strip()
            action = lines.pop(0).split('POTOM', 1)[1].strip()
            rules.append(Rule(name, requirement, action))
        return rules

    @staticmethod
    def _fill(string, values):
        for v in values:
            string = string.replace('?' + v, values[v])
        return string

    def create_actions(self, facts):
        requirements = []
        eval_requirements = []
        values = []

        for r in self.requirements:
            if r.startswith('eval'):
                eval_requirements.append(r.replace('eval ', ''))
            else:
                requirements.append(r)

        for r in requirements:
            sub = re.sub('\?(.)', '(?P<\\1>.+)', r)
            v = [re.match(sub, f).groupdict() for f in facts if re.match(sub, f)]
            values.append(v)

        if len(values) == len(requirements):
            prod = itertools.product(*values)
            values = []
            for dicts in prod:
                merged_dict = {}
                valid = True
                for d in dicts:
                    for key in d:
                        if key not in merged_dict:
                            merged_dict[key] = d[key]
                        elif merged_dict[key] != d[key]:
                            valid = False
                if valid and all([eval(self._fill(r, merged_dict)) for r in eval_requirements]):
                    values.append(merged_dict)

        return [[
            re.sub('eval ([\-0-9]+ [\+\-\*/] [\-0-9]+)',
                   lambda match: str(eval(match.group(1))),
                   self._fill(a, v)) for a in self.actions
        ] for v in values]


class Fact:
    @staticmethod
    def read(file_name):
        with open(file_name) as f:
            lines = [l.strip() for l in f.read().splitlines() if l.strip()]
        facts = [x.replace('(', '').replace(')', '') for x in lines]
        return facts


def filter_actions(actions, facts):
    filtered_actions = []
    for action_sequence in actions:
        for action in action_sequence:
            a, f = action.split(' ', 1)
            if (a == 'pridaj' and f in facts) or (a == 'vymaz' and f not in facts):
                action_sequence.remove(action)
        if len(action_sequence) > 0 and not all(x.startswith('sprava') for x in action_sequence):
            filtered_actions.append(action_sequence)
    return filtered_actions


def process_action(action_sequence, facts):
    for action in action_sequence:
        a, f = action.split(' ', 1)
        if a == 'pridaj':
            facts.append(f)
        elif a == 'vymaz':
            facts.remove(f)
        elif a == 'sprava':
            print(f)


def solve(rules_file, facts_file):
    # Nacitanie pravidiel a faktov
    rules = Rule.read(rules_file)
    facts = Fact.read(facts_file)

    print('Vystup sprav:')
    while True:
        # Vygenerujeme vsetky mozne aplikovatelne instancie pravidiel
        actions = []
        for rule in rules:
            actions += rule.create_actions(facts)
            actions += rule.create_actions(facts)

        # Odfiltrujeme pravidla ktore nezmenia pracovnu pamat
        actions = filter_actions(actions, facts)

        # Ak nie je ziadna aplikovatelna instancia pravidla tak koncime
        if not actions:
            break

        # Pouzijeme prvu instanciu prveho pravidla
        process_action(actions[0], facts)

    # Na konci vypiseme vysledny stav pracovnej pamati
    print('\nPracovna pamat:')
    for fact in facts:
        print(fact)


if __name__ == '__main__':
    print(80 * '=')
    print('Rodina:')
    print(80 * '=')
    solve('rodina_pravidla.txt', 'rodina_fakty.txt')
    print(80 * '=')
    print("Faktorial:")
    print(80 * '=')
    solve('faktorial_pravidla.txt', 'faktorial_fakty.txt')