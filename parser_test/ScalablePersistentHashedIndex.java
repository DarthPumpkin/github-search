/*
 *   This file is part of the computer assignment for the
 *   Information Retrieval course at KTH.
 *
 *   Johan Boye, KTH, 2018
 */

package ir;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.stream.Stream;

/*
 *   Implements an inverted index as a hashtable on disk.
 *
 *   Both the words (the dictionary) and the data (the postings list) are
 *   stored in RandomAccessFiles that permit fast (almost constant-time)
 *   disk seeks.
 *
 *   When words are read and indexed, they are first put in an ordinary,
 *   main-memory HashMap. When all words are read, the index is committed
 *   to disk.
 */
public class ScalablePersistentHashedIndex implements Index {
    private static final String TOKENS_FNAME = "tokens";
    public static final List<String> METADATA_FNAMES = List.of(PersistentHashedIndex.DOCINFO_FNAME, TOKENS_FNAME);
    public static final List<String> INDEX_FNAMES = List.of(TOKENS_FNAME,
            PersistentHashedIndex.DOCINFO_FNAME,
            PersistentHashedIndex.DATA_FNAME,
            PersistentHashedIndex.DICTIONARY_FNAME);
    private static final int MAX_TOKENS = 5_000_000;
    //    private PersistentHashedIndex fullIndex;
    private PersistentHashedIndex inMemoryIndex;
    private int subIndexId = -1;
    private int currentDocId = 0;
    private Thread currentMerge = null;
    private boolean clean = true;  // clean for getPostings()


    public ScalablePersistentHashedIndex() {
//        fullIndex = new PersistentHashedIndex();
        inMemoryIndex = new PersistentHashedIndex();
        if (inMemoryIndex.docNames.isEmpty()) {
            newSubIndex();
        }
    }

    @Override
    public HashMap<Integer, String> docNames() {
//        return fullIndex.docNames;
        return inMemoryIndex.docNames;
    }

    @Override
    public HashMap<Integer, Integer> docLengths() {
//        return fullIndex.docLengths;
        return inMemoryIndex.docLengths;
    }

    @Override
    public void insert(String token, int docID, int offset) {
        clean = false;
        if (docID != currentDocId) {
            currentDocId = docID;
            if (isSubIndexFull()) {
                writeSubIndex();
                newSubIndex();
            }
        }
        inMemoryIndex.insert(token, docID, offset);
    }

    @Override
    public Stream<String> streamTokens() throws IOException {
        return inMemoryIndex.streamTokens();
    }

    @Override
    public PostingsList getPostings(String token) {
        if (!clean)
            throw new IllegalStateException();
        return inMemoryIndex.getPostings(token);
    }

    @Override
    public void cleanup() {
        writeSubIndex();
        try {
            currentMerge.join();
            System.err.println("All merges complete");
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        inMemoryIndex = new PersistentHashedIndex();
        clean = true;
        System.err.println("Indexing complete");
    }

    private boolean isSubIndexFull() {
        int numTokens = docLengths().values().stream().mapToInt(x -> x).sum();
        return numTokens > MAX_TOKENS;
    }

    private void writeSubIndex() {
        System.err.println("Writing index to disk with id " + subIndexId);
        inMemoryIndex.cleanup();
        System.err.println("Wrote index to disk with id " + subIndexId);
        if (subIndexId > 0) {   // merge the two indexes
            Thread newMerge = new Thread(new Merge(subIndexId, currentMerge, inMemoryIndex));
            System.err.println("Starting new write+merge thread");
            newMerge.start();
            currentMerge = newMerge;
        }
    }

    private void newSubIndex() {
        subIndexId++;
        String suffix = (subIndexId == 0) ? "" : "_" + subIndexId;
        inMemoryIndex = new PersistentHashedIndex(suffix);
//        inMemoryIndex.docNames = fullIndex.docNames;
//        inMemoryIndex.docLengths = fullIndex.docLengths;
    }
}
