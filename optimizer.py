#!/usr/bin/env python3
# completed by dongchangzhang
# 2017.6.2

from graphviz import *

sql1 = "SELECT [ ENAME = 'Mary' & DNAME = 'Research' ] ( EMPLOYEE JOIN DEPARTMENT )"
sql2 = "PROJECTION [ BDATE ] ( SELECT [ ENAME = 'John' & DNAME = 'Research' ] ( EMPLOYEE JOIN DEPARTMENT ) )"
sql3 = "SELECT [ ESSN = '01' ] ( PROJECTION [ ESSN , PNAME ] ( WORKS_ON JOIN PROJECT ) )"

key_words = ('SELECT', 'PROJECTION', )

class Node:
    '''
    <action, info>
    action: select, projection
    info: column1 = 'value1' and column2 = 'value2'...
    '''
    def __init__(self, element, infos, flag=False, rel=None):
        if flag:
            self.singel(element, infos, rel)
        else:
            self.all(element, infos)
    def singel(self, element, infos, rel):
        self.node = element
        self.infos = [infos, ]
        self.rel = rel
    def all(self, element, infos):
        self.element = element
        if element == 'SELECT':
            self.node = ''
            self.rel = ' and '
        elif element == 'PROJECTION':
            self.node = ''
            self.rel = ' ,'
        else:
            self.node = 'Error'
            self.rel = ' '
        tmp = ''
        self.infos = []
        for i in infos:
            if i != '[' and i != ']':
                if i == ',':
                    self.infos.append(tmp)
                    tmp = ''
                elif i == '&':
                    self.infos.append(tmp)
                    tmp = ''
                else:
                    tmp += i
        if tmp != '':
            self.infos.append(tmp)

    def __str__(self):
        return '%s %s' % (self.node, self.rel.join(self.infos))
    def __repr__(self):
        return '%s, %s' % (self.node, self.rel.join(self.infos))
    def get_label(self):
        return '%s %s' % (self.node, self.rel.join(self.infos))
    def split(self):
        return [Node(self.node, x, True, self.rel) for x in self.infos]
    def of_type(self):
        if self.node ==  '':
            return 'select'
        elif self.node == '':
            return 'projection'
        else:
            return None
    def get_info(self):
        return self.infos[0]

def get_action(index, elements):
    '''
    dealing < select [ rules ] > or < projection [ columns ] >
    '''
    if elements[index] == 'SELECT' or elements[index] == 'PROJECTION':
        infos = []
        element = elements[index]
        while index < len(elements) and elements[index] != ']':
            index += 1
            infos.append(elements[index])
        node = Node(element, infos)
    return index + 1, node

def get_table(index, elements):
    '''
    dealing < (table join table) > or < (table) >
    table -> tablename
    table -> < select [rules] (table) >
    table -> < projection [columns] (table) >
    '''
    nodes = []
    tree = {}
    parent = -1
    in_nest = 0
    have_join = False
    have_slt_pjt = False
    for i in range(index, len(elements)):
        if elements[i] == '(':
            in_nest += 1
        elif elements[i] == ')':
            in_nest -= 1
        if in_nest == 0:
            if elements[i] in key_words:
                have_slt_pjt = True
            elif elements[i] == 'JOIN':
                have_join = True
    if have_join == True and have_slt_pjt == False:
        tree[parent] = 0
        parent = 0
        nodes.append('⋈')
        while index < len(elements) and elements[index] != ')':
            if elements[index] != 'JOIN':
                try:
                    tree[parent].append(len(nodes))
                except:
                    tree[parent] = [len(nodes),]
                nodes.append(elements[index])
            index += 1
    elif have_join == False and have_slt_pjt == True:
        if elements[index] == 'SELECT' or elements[index] == 'PROJECTION':
            index, node = get_action(index, elements)
            tree[parent] = len(nodes)
            parent = len(nodes)
            nodes.append(node)
            index, new_nodes, new_tree = get_table(index + 1, elements)
            width = len(nodes)
            nodes.extend(new_nodes)
            for key, value in new_tree.items():
                if key == -1:
                    tree[parent] = value + width
                if type(value) is list:
                    tree[key + width] = [x + width for x in value]
                else:
                    tree[key + width] = value + width

    return index + 1, nodes, tree


def create_tree(sql):
    '''
    call get_action and then call get_table
    '''
    parent = -1
    tree = {}
    nodes = []
    elements = sql.split(' ')
    index, node = get_action(0, elements)
    tree[-1] = 0
    parent = 0
    nodes.append(node)
    index, new_nodes, new_tree = get_table(index + 1, elements)
    width = len(nodes)
    nodes.extend(new_nodes)
    for key, value in new_tree.items():
        if key == -1:
            tree[parent] = value + width
        if type(value) is list:
            tree[key + width] = [x + width for x in value]
        else:
            tree[key + width] = value + width
    return nodes, tree

def optimize(nodes, tree):
    nexts = -1
    loc_select = find_in_tree(nodes, tree, nexts, 'select', True)
    if loc_select != None:
        print(loc_select)
        nexts = tree[loc_select]
        nodes, tree = optimize_select(nodes, tree, loc_select)
    return nodes, tree


def optimize_select(nodes, tree, loc):
    print(nodes, tree)
    node = nodes[tree[loc]]
    tmp = node.split()
    tree[loc] = tree.pop(tree[loc])
    loc = find_in_tree(nodes, tree, -1, '⋈')
    indexes = tree[tree[loc]][::]
    for select_node in tmp:
        for index in indexes:
            node = nodes[index]
            if node[0] == select_node.get_info()[0] or (node[0] == 'W' and select_node.get_info()[0] == 'E'):
                tree[tree[loc]].remove(index)
                tree[tree[loc]].append(len(nodes))
                tree[len(nodes)] = index
                nodes.append(select_node)
    return nodes, tree

def find_in_tree(nodes, tree, parent, target, is_node=False):
    '''
    find a node in the tree and then return the location of node's parent
    '''
    if parent not in tree:
        return None
    indexes = tree[parent]
    if type(indexes) is list:
        for index in indexes:
            node = nodes[index]
            if is_node and type(node) is Node:
                if node.of_type() == target:
                    return parent
            elif node == target:
                return parent
            return find_in_tree(nodes, tree, index, target, is_node)
    else:
        node = nodes[indexes]
        if is_node and type(node) is Node:
            if node.of_type() == target:
                return parent
        elif node == target:
                return parent
        return find_in_tree(nodes, tree, indexes, target, is_node)

def draw_tree(nodes, tree, name, comment):
    '''
    show the tree by graphviz
    '''
    tmp = []
    dot = Digraph(comment=comment)
    dot.node('name', comment, shape='rectangle')
    for key, value in tree.items():
        if key != -1 and key not in tmp:
            tmp.append(key)
        if type(value) is list:
            for i in value:
                if i not in tmp:
                    tmp.append(i)
        else:
            if value not in tmp:
                tmp.append(value)
    for i in tmp:
        if type(nodes[i]) is Node:
            info = nodes[i].get_label()
        else:
            info = nodes[i]
        dot.node(str(i), info)
    for key, value in tree.items():
        if key == -1:
            continue
        if type(value) is list:
            for j in value:
                dot.edge(str(key), str(j))
        else:
            dot.edge(str(key), str(value))
    dot.render('./tree%s.gv' % name, view=True)


def run(sql, i, comment):
    '''
    analysis sql
    and then optimize it
    '''
    nodes, tree = create_tree(sql)
    draw_tree(nodes, tree, i, comment)
    nodes, tree = optimize(nodes, tree)
    draw_tree(nodes, tree, '%s_optimize' % i, '优化后 %s' % comment)


if __name__ == '__main__':
    op = input()
    print(op)
    if op == '1':
        run(sql1, 1, sql1)
    elif op == '2':
        run(sql2, 2, sql2)
    elif op == '3':
        run(sql3, 3, sql3)
    else:
        print('Error')
