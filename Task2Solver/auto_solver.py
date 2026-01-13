import itertools
from typing import List, Tuple, Optional


class LogicSolver:
    def __init__(self, fragment: List[List[Optional[bool]]],
                 results: List[bool],
                 expression: str,
                 variables: List[str]) -> None:
        """
        :param fragment: Фрагмент таблицы (None - пустая ячейка, True/False - значения).
        :param results: Столбец результатов F.
        :param expression: Выражение на языке Python (например: 'x and y or not z').
        :param variables: Список имен переменных ['x', 'y', 'z'].
        """
        self.fragment = fragment
        self.results = results
        self.expression = expression
        self.variables = variables
        self.n_vars = len(variables)

    def _evaluate(self, values: Tuple[int, ...], var_names: Tuple[str, ...]) -> bool:
        context = dict(zip(var_names, values))
        try:
            return bool(eval(self.expression, {}, context))
        except Exception:
            return False

    def _generate_full_table(self) -> List[Tuple[Tuple[int, ...], bool]]:
        all_inputs = list(itertools.product([0, 1], repeat=self.n_vars))
        table = []
        for row in all_inputs:
            res = self._evaluate(row, tuple(self.variables))
            table.append((row, res))
        return table

    def _rows_match(self, fragment_row: List[Optional[bool]], full_row: Tuple[int, ...]) -> bool:
        """
        Проверяет совместимость строки фрагмента и строки полной таблицы.
        """
        for f_val, full_val in zip(fragment_row, full_row):
            if f_val is not None and f_val != full_val:
                return False
        return True

    def solve(self) -> str:
        full_table = self._generate_full_table()

        col_indices = range(self.n_vars)

        for perm in itertools.permutations(col_indices):

            is_permutation_valid = True

            for i, frag_row_vals in enumerate(self.fragment):
                frag_result = self.results[i]

                found_match_in_full_table = False

                for real_row_vals, real_res in full_table:
                    if real_res != frag_result:
                        continue

                    permuted_row = tuple(real_row_vals[perm[k]] for k in range(self.n_vars))

                    if self._rows_match(frag_row_vals, permuted_row):
                        found_match_in_full_table = True
                        break

                if not found_match_in_full_table:
                    is_permutation_valid = False
                    break

            if is_permutation_valid:
                return ''.join([self.variables[idx] for idx in perm])

        return "Solution not found"