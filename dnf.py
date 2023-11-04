from itertools import product
from functools import reduce


class PredicateFormula:
    ''' 谓词公式类 '''
    LOGIC_VAR_ALPHA = tuple(chr(i) for i in range(97, 123))     # 合法逻辑变量名称
    OPERATOR = ('+', '*', '!')
    CHARACTER = LOGIC_VAR_ALPHA + OPERATOR + ('(', ')', ' ')
    INSTACK_PRIORITY = {'+': 3, '*': 5, '!': 6, '(': 1, ')': 10}
    INCOMING_PRIORITY = {'+': 2, '*': 4, '!': 7, '(': 10, ')': 1}

    def __init__(self, origin: str=None):
        # 输入的字符串
        if origin is None:
            self.origin = ''
        elif self.is_legal(origin):
            self.origin = origin
        else:
            raise Exception('expression include illegal logic variable')
        self.processed = ''                                     # 经处理后的字符串
        self.postfix_exp = ''                                   # 后缀表达式
        self.pdnf = ''                                          # 主析取范式
        self.logic_var = []                                     # 输入字符串中的逻辑变量
        self.truth_table = {}                                   # 真值表
        self.sigma = set()                                      # 命题公式极小项

    @classmethod
    def is_legal(cls, formula: None) -> bool:
        for c in formula:
            if c not in cls.CHARACTER:
                return False
        return True

    @classmethod
    def get_isp(cls, content: str):
        return  cls.INSTACK_PRIORITY.get(content)

    @classmethod
    def get_icp(cls, content: str):
        return  cls.INCOMING_PRIORITY.get(content)

    def set_formula(self, formula: str=None) -> str:
        ''' set the original formulation '''
        if formula is None:
            return None
        if not self.is_legal(formula=formula):
            raise Exception('illegal expression')
        self.origin = formula
        return self.origin

    def extract_variable(self) -> list:
        ''' extract all logic variable from formula '''
        if self.origin == '':
            raise Exception('expression can not be null')
        if not self.is_legal(self.origin):
            raise Exception('Can not cognize and parse expression')
        logic_vars = []

        for chars in self.origin:
            if (chars in self.LOGIC_VAR_ALPHA 
                and chars not in logic_vars):            # 输入字符串格式判定
                logic_vars.append(chars)                 # 将逻辑变量存入列表

        logic_vars.sort()
        self.logic_var = logic_vars
        return logic_vars

    def process_formula(self) -> str:
        ''' process formula: 
            include complement, replace, conversion '''
        self.extract_variable()

        origin = self.origin
        process = []

        for i in range(len(origin)-1):
            if str.isspace(origin[i]):
                continue
            process.append(origin[i])
            if len(process) >= 2 and process[-1] == '!' and process[-2] == '!':
                process.pop(); process.pop()
            if (origin[i] in (*self.logic_var, ')')
                and origin[i+1] in (*self.logic_var, '(', '!')):
                process.append('*')
        process.append(origin[-1])
        
        process = ''.join(process)
        self.processed = process
        return process

    def to_postfix_exp(self) -> list[str]:
        ''' convertion to postfix expression '''
        self.process_formula()

        stack = []
        postfix_expression = []

        for c in self.processed:
            if c in self.logic_var:
                postfix_expression.append(c)
                continue
            # 比较栈内栈外优先级判断出栈入栈
            while len(stack) != 0 and self.get_icp(c) <= self.get_isp(stack[-1]):
                postfix_expression.append(stack.pop())
            if len(stack) != 0 and stack[-1] == '(':
                stack.pop()
            if c != ')':
                stack.append(c)

        while len(stack) != 0:
            postfix_expression.append(stack.pop())

        self.postfix_exp = postfix_expression
        return postfix_expression

    def calc_postfix_exp(self, logic_var_value: dict[str: bool]) -> bool:
        ''' calculate the postfix expression '''
        self.to_postfix_exp()

        stack = []
        postfix_expression = self.postfix_exp

        for c in postfix_expression:
            if c in self.logic_var:
                stack.append(logic_var_value[c])
            elif c == '!':
                stack.append(not stack.pop())
            elif c == '*':
                stack.append(stack.pop() and stack.pop())
            elif c == '+':
                stack.append(stack.pop() or stack.pop())

        if len(stack) == 0:
            raise Exception('expression syntax error')
        return stack.pop()

    def calc_truth_table(self) -> list[tuple[dict, bool]]:
        ''' according to the postfix expression to calculate truth table '''
        self.to_postfix_exp()

        if len(self.logic_var) > 10:
            raise Exception('too many variable to process')
            return None

        # 返回所有可能逻辑输入
        prd = product(* ((False, True) for _ in self.logic_var))
        var_value = tuple(dict(zip(self.logic_var, val)) for val in prd)
        truth_table = []

        # 计算真值表
        for v in var_value:
            truth_table.append((v, self.calc_postfix_exp(v)))

        self.truth_table = truth_table
        return truth_table

    def truth_table_print(self, fold: bool=True, fold_line: int=10) -> None:
        ''' print truth table in format '''
        self.calc_truth_table()

        if fold == True:
            prompt = '......' if fold_line < len(self.truth_table) else ''
            line = min(len(self.truth_table), fold_line)
        else:
            prompt = ''
            line = len(self.truth_table)

        for var in self.logic_var:
            print(f'{var:>6}', end='')
        print('     %s'%'Truth Value')
        print('-' * (6 * (len(self.logic_var) + 1) + 16))

        for i in range(line):
            for var, num in self.truth_table[i][0].items():
                print(f'{num:>6}', end='')
            print('     %s'%self.truth_table[i][1])
        print(f'{prompt}')

    def parse(self) -> bool:
        ''' extract sigma to solve disjuction formula.
            if success, return true; else, return false '''
        self.calc_truth_table()

        for record in self.truth_table:
            sigma = ''
            if not record[1]:
                continue

            for var, num in record[0].items():
                if num:
                    sigma += var
                else:
                    sigma += '!' + var

            self.sigma.add(sigma)

        # 合并极小项
        self.pdnf = reduce(lambda a, b: a + '+' + b,
                        self.sigma) if len(self.sigma) != 0 \
                        else 'Contradictory Formula'
        return True

    def __eq__(self, __value: object) -> bool:
        if type(self) != type(__value):
            return False

        self.parse()
        __value.parse()

        return self.sigma == __value.sigma

    @classmethod
    def equal(cls, pfml, other):
        if type(pfml) != cls or type(other) != cls:
            return False
        return pfml.origin == other.origin

    def __str__(self) -> str:
        return f'{super.__str__(self)}  Origin formula: {self.origin}'

