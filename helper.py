def generate_postcodes():
    postcode_ranges = {
        'NSW': [(2000, 2599), (2619, 2899), (2921, 2999)],
        'ACT': [(2600, 2618), (2900, 2920)],
        'VIC': [(3000, 3999)],
        'QLD': [(4000, 4999)],
        'SA': [(5000, 5799)],
        'WA': [(6000, 6797)],
        'TAS': [(7000, 7799)],
        'NT': [(800, 899)]
    }

    valid_postcodes = []

    for state, ranges in postcode_ranges.items():
        for start, end in ranges:
            valid_postcodes.extend([str(code).zfill(4) for code in range(start, end + 1)])

    return valid_postcodes