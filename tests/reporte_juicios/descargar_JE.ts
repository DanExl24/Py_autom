import { go_to_menu, goto_menu_child } from "./go_to_menus";

export const descargar_juicios_fichas = async () => {
  await go_to_menu("Ejecución de la Formación");
  await goto_menu_child(
    await go_to_menu("Administrar Ruta de Aprendizaje "),
    "Reportes ",
  );
  await go_to_menu("Reporte de Juicios de Evaluación");
};
