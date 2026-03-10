# expense_processor
Process credit and banks statements to calculate monthly expenses
</br> rough lay out:
</br> - first load statements into iterable lists/dictionaries
</br> - load known classifications
</br> - compare statement data to known classifications and write formatted data to something for output
</br> - look into fuzzy matching to see how to use (rapidfuzz package). am i already doing this through dataframes?
</br> - output the list of unclassified transactions - worst case feed into ai manually but can i do that programmatically?
</br> 
</br> 
</br> QUESTION:
</br> - are dataframes the most efficient and lowest overhead way to do this?
</br> - not sure if i should remove credit payments on credit card statements from output_df. I did in the original but is that necessary? it'll depend on how its calculated in google sheets