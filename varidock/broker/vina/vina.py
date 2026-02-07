from vina import Vina


def dock(
    receptor_pdbqt: str,
    ligand_pdbqt: str,
    center: tuple[float, float, float],
    output_poses: str,
    output_log: str,
    output_minimize: str | None = None,
    box_size: tuple[float, float, float] = (20.0, 20.0, 20.0),
    exhaustiveness: int = 32,
    write_n_poses: int = 5,
    dock_n_poses: int = 20,
    scoring_function: str = "vina",
) -> list[float]:
    """Run AutoDock Vina docking. Returns list of affinity scores."""
    v = Vina(sf_name=scoring_function)
    v.set_receptor(receptor_pdbqt)
    v.set_ligand_from_file(ligand_pdbqt)
    v.compute_vina_maps(center=list(center), box_size=list(box_size))

    score_before = v.score()[0]
    score_after = v.optimize()[0]

    if output_minimize:
        v.write_pose(output_minimize, overwrite=True)

    v.dock(exhaustiveness=exhaustiveness, n_poses=dock_n_poses)
    v.write_poses(output_poses, n_poses=write_n_poses, overwrite=True)

    energies = v.energies(n_poses=dock_n_poses)
    affinities = [e[0] for e in energies]

    with open(output_log, "w") as f:
        f.write(f"Score before minimization: {score_before:.3f} (kcal/mol)\n")
        f.write(f"Score after minimization : {score_after:.3f} (kcal/mol)\n\n")
        f.write("mode |   affinity | dist from best mode\n")
        f.write("     | (kcal/mol) | rmsd l.b.| rmsd u.b.\n")
        f.write("-----+------------+----------+----------\n")
        for i, e in enumerate(energies):
            f.write(f"   {i + 1:2d}      {e[0]:7.3f}     {e[1]:6.4f}     {e[2]:6.3f}\n")

    return affinities
