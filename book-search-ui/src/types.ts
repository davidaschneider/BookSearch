import { ReactNode } from "react";

export type BookData = {
	authors: Array<string>,
	title: string,
	cover_url: string | null,
	formats: Array<string> | null,
	/**
	 * There should always be one of these, but in practice sometimes there isn't.
	 */
	isbn: string | null,
	publish_year: string | null,
	summary: string | ReactNode | null,
	/** 
	 * If true, it is assumed that no calls will ever be needed to have the server
	 * gather more information, since any and all supplemental information has already been added.
	 */
	fully_enriched: boolean,
}

export const LOADING = "**Loading**"