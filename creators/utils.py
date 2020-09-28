
def _make_alternative_in_seq(map, seq_list, upper_excludes=None):
    for seq in seq_list:
        if isinstance(seq, list):
            _make_alternative_in_choice(map, seq, upper_excludes)
        else:
            excludes = []
            if upper_excludes:
                excludes.extend(upper_excludes)
            map[seq] = excludes


def _make_alternative_in_choice(map, choice_list, upper_excludes=None):
    for choice in choice_list:
        sub_list = list(filter(lambda x: x is not choice, choice_list))
        excludes = []
        _make_plane_list(excludes, sub_list)

        if isinstance(choice, list):
            _make_alternative_in_seq(map, choice, upper_excludes=excludes)
        else:
            if upper_excludes:
                excludes.extend(upper_excludes)
            map[choice] = excludes


def _make_plane_list(container, rows):
    for row in rows:
        if isinstance(row, list):
            _make_plane_list(container, row)
        else:
            container.append(row)
