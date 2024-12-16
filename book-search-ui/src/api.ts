import { BookData } from "types";

export const bookSearch = async (searchText: string, page:number = 1): Promise<{total_available: number, books: Array<BookData>}> => {
	let url = `search?title=${encodeURIComponent(searchText)}&page=${page}`
	const resp = await fetch(url);
	if (!resp.ok) {
		console.log("No search result from " + url)
		console.warn(resp.body)
	}
	return await resp.json();
}

export const isbnLookup = async (isbn: string[], fields: string[] = []): Promise<Array<BookData>> => {
	let url = `book?isbn=${JSON.stringify(isbn)}&fields=${JSON.stringify(fields)}`
	const resp = await fetch(url);
	if (!resp.ok) {
		console.log("No data from from ISBN " + isbn)
		console.warn(resp.body)
		throw new Error("Unable to retrieve data for " + isbn)
	}
	return await resp.json();
}